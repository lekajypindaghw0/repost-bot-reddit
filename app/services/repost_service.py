import json
import os
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import praw

from app.core.config import settings
from app.core.logger import get_logger
from app.services.rate_limiter import RateLimiter
from app.services.similarity_engine import compare

log = get_logger("repost-service")

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _safe_filename(s: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in s)[:120]

CANDIDATES_DIR = os.path.join(settings.DATA_DIR, "candidates")
CHECKS_DIR = os.path.join(settings.DATA_DIR, "checks")
DRAFTS_DIR = os.path.join(settings.DATA_DIR, "drafts")

for d in (CANDIDATES_DIR, CHECKS_DIR, DRAFTS_DIR):
    os.makedirs(d, exist_ok=True)

@dataclass
class CheckJob:
    job_id: str
    status: str
    subreddits: List[str]
    lookback_days: int
    min_title_similarity: float
    started_at: str
    finished_at: Optional[str]
    candidate_path: str
    result_path: str

class RepostAssistantService:
    """Repost workflow assistant.

    This service:
    - Accepts 'candidate' content (title + optional URL)
    - Searches subreddit history (read-only) within a lookback window
    - Produces a ranked list of potential duplicates with scores
    - Generates a draft payload (for human review) when safe to proceed

    It intentionally does NOT post to Reddit.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._jobs: Dict[str, CheckJob] = {}
        self._threads: Dict[str, threading.Thread] = {}

        # If creds are missing, PRAW can still be instantiated for limited public access,
        # but authenticated is recommended.
        self._reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID or None,
            client_secret=settings.REDDIT_CLIENT_SECRET or None,
            username=settings.REDDIT_USERNAME or None,
            password=settings.REDDIT_PASSWORD or None,
            user_agent=settings.REDDIT_USER_AGENT,
        )

    def start_check(
        self,
        candidate: Dict[str, Any],
        subreddits: List[str],
        lookback_days: Optional[int] = None,
        min_title_similarity: Optional[float] = None,
    ) -> str:
        with self._lock:
            active = sum(1 for j in self._jobs.values() if j.status in ("running", "starting"))
            if active >= settings.MAX_ACTIVE_JOBS:
                raise RuntimeError(f"Too many active jobs (max={settings.MAX_ACTIVE_JOBS}).")

        job_id = uuid.uuid4().hex[:12]
        subreddits = subreddits or [s.strip() for s in settings.DEFAULT_SUBREDDITS.split(",") if s.strip()]
        lb = int(lookback_days or settings.LOOKBACK_DAYS)
        mts = float(min_title_similarity or settings.MIN_TITLE_SIMILARITY)

        cand_path = os.path.join(CANDIDATES_DIR, f"{_safe_filename(job_id)}.json")
        res_path = os.path.join(CHECKS_DIR, f"{_safe_filename(job_id)}_results.json")

        with open(cand_path, "w", encoding="utf-8") as f:
            json.dump({"candidate": candidate, "created_at": _utc_now_iso()}, f, ensure_ascii=False, indent=2)

        job = CheckJob(
            job_id=job_id,
            status="starting",
            subreddits=subreddits,
            lookback_days=lb,
            min_title_similarity=mts,
            started_at=_utc_now_iso(),
            finished_at=None,
            candidate_path=cand_path,
            result_path=res_path,
        )
        with self._lock:
            self._jobs[job_id] = job

        t = threading.Thread(target=self._run_check, args=(job_id,), daemon=True, name=f"check-{job_id}")
        self._threads[job_id] = t
        t.start()
        return job_id

    def get_job(self, job_id: str) -> CheckJob:
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError("job not found")
            return self._jobs[job_id]

    def list_jobs(self) -> List[CheckJob]:
        with self._lock:
            return list(self._jobs.values())

    def read_results(self, job_id: str) -> Dict[str, Any]:
        job = self.get_job(job_id)
        if not os.path.exists(job.result_path):
            return {"job_id": job_id, "status": job.status, "results": []}
        with open(job.result_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _iter_subreddits(self, subs: List[str]):
        if len(subs) == 1 and subs[0].lower() == "all":
            yield self._reddit.subreddit("all")
            return
        for s in subs:
            s = s.strip()
            if not s:
                continue
            yield self._reddit.subreddit(s)

    def _run_check(self, job_id: str) -> None:
        limiter = RateLimiter(min_interval_seconds=1.0)
        with self._lock:
            job = self._jobs[job_id]
            job.status = "running"

        try:
            with open(job.candidate_path, "r", encoding="utf-8") as f:
                candidate_doc = json.load(f)
            candidate = candidate_doc.get("candidate", {})
            cand_title = candidate.get("title", "") or ""
            cand_url = candidate.get("url")

            cutoff = datetime.now(timezone.utc) - timedelta(days=job.lookback_days)
            cutoff_ts = cutoff.timestamp()

            hits: List[Dict[str, Any]] = []

            for sr in self._iter_subreddits(job.subreddits):
                # Use Reddit search by title keywords if present; fall back to 'new'
                query_terms = " ".join((cand_title or "").split()[:8])
                if query_terms:
                    search_iter = sr.search(query_terms, sort="new", time_filter="year", limit=settings.MAX_RESULTS_PER_QUERY)
                else:
                    search_iter = sr.new(limit=settings.MAX_RESULTS_PER_QUERY)

                for sub in search_iter:
                    limiter.wait()
                    try:
                        created = float(getattr(sub, "created_utc", 0.0) or 0.0)
                    except Exception:
                        created = 0.0
                    if created and created < cutoff_ts:
                        continue

                    hit_title = getattr(sub, "title", "") or ""
                    hit_url = getattr(sub, "url", None)
                    sim = compare(cand_title, cand_url, hit_title, hit_url)

                    # Keep candidates if URL matches or title similarity is high enough
                    if sim.same_url or sim.title_score >= job.min_title_similarity:
                        hits.append({
                            "subreddit": str(getattr(sub, "subreddit", "")),
                            "id": getattr(sub, "id", None),
                            "permalink": f"https://www.reddit.com{getattr(sub, 'permalink', '')}",
                            "title": hit_title,
                            "url": hit_url,
                            "created_utc": created,
                            "title_similarity": round(sim.title_score, 4),
                            "same_url": sim.same_url,
                        })

            # Rank: URL matches first, then by title similarity
            hits.sort(key=lambda x: (x["same_url"], x["title_similarity"]), reverse=True)

            # Draft: only produce a "ready" draft if no strong duplicates
            strong_dupes = [h for h in hits if h["same_url"] or h["title_similarity"] >= max(job.min_title_similarity, 0.9)]
            draft = {
                "title": cand_title.strip()[:300],
                "url": cand_url,
                "notes": candidate.get("notes"),
                "status": "needs_review" if strong_dupes else "draft_ready",
                "recommendation": "Review similar posts before posting." if strong_dupes else "No strong duplicates found in lookback window.",
                "generated_at": _utc_now_iso(),
            }

            # Save result
            out = {
                "job_id": job_id,
                "status": "completed",
                "subreddits": job.subreddits,
                "lookback_days": job.lookback_days,
                "min_title_similarity": job.min_title_similarity,
                "candidate": candidate,
                "results": hits[:200],
                "draft": draft,
                "completed_at": _utc_now_iso(),
            }
            with open(job.result_path, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)

            # Also save draft separately
            draft_path = os.path.join(DRAFTS_DIR, f"{_safe_filename(job_id)}_draft.json")
            with open(draft_path, "w", encoding="utf-8") as f:
                json.dump(draft, f, ensure_ascii=False, indent=2)

            with self._lock:
                job = self._jobs[job_id]
                job.status = "completed"
                job.finished_at = _utc_now_iso()

            log.info("job %s completed | hits=%d | draft=%s", job_id, len(hits), draft.get("status"))

        except Exception as e:
            log.exception("job %s failed: %s", job_id, e)
            with self._lock:
                job = self._jobs[job_id]
                job.status = "failed"
                job.finished_at = _utc_now_iso()

repost_service = RepostAssistantService()
