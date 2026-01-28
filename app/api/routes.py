from fastapi import APIRouter, HTTPException
from app.api.schemas import StartCheckRequest, StartCheckResponse, JobStatusResponse, ResultsResponse
from app.services.repost_service import repost_service

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/checks/start", response_model=StartCheckResponse)
def start_check(req: StartCheckRequest):
    try:
        job_id = repost_service.start_check(
            candidate=req.candidate.dict(),
            subreddits=req.subreddits,
            lookback_days=req.lookback_days,
            min_title_similarity=req.min_title_similarity,
        )
        return {"job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/checks", response_model=list[JobStatusResponse])
def list_checks():
    return [j.__dict__ for j in repost_service.list_jobs()]

@router.get("/checks/{job_id}", response_model=JobStatusResponse)
def get_check(job_id: str):
    try:
        job = repost_service.get_job(job_id)
        return job.__dict__
    except KeyError:
        raise HTTPException(status_code=404, detail="job not found")

@router.get("/checks/{job_id}/results", response_model=ResultsResponse)
def get_results(job_id: str):
    try:
        data = repost_service.read_results(job_id)
        return data
    except KeyError:
        raise HTTPException(status_code=404, detail="job not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
