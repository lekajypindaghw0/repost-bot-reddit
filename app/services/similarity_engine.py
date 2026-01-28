import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional

_WS = re.compile(r"\s+")
_NONWORD = re.compile(r"[^a-z0-9\s]+")

def normalise_title(title: str) -> str:
    title = (title or "").lower()
    title = _NONWORD.sub(" ", title)
    title = _WS.sub(" ", title).strip()
    return title

def title_similarity(a: str, b: str) -> float:
    a_n = normalise_title(a)
    b_n = normalise_title(b)
    if not a_n or not b_n:
        return 0.0
    return SequenceMatcher(None, a_n, b_n).ratio()

def normalise_url(url: str) -> str:
    url = (url or "").strip()
    url = url.replace("http://", "https://")
    # strip tracking/query fragments that often don't matter for repost checks
    url = url.split("#", 1)[0]
    return url

@dataclass
class SimilarityResult:
    title_score: float
    same_url: bool

def compare(candidate_title: str, candidate_url: Optional[str], hit_title: str, hit_url: Optional[str]) -> SimilarityResult:
    tscore = title_similarity(candidate_title, hit_title)
    cu = normalise_url(candidate_url or "")
    hu = normalise_url(hit_url or "")
    same_url = bool(cu and hu and cu == hu)
    return SimilarityResult(title_score=tscore, same_url=same_url)
