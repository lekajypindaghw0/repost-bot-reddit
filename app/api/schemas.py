from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

class Candidate(BaseModel):
    title: str = Field(..., min_length=3, max_length=300)
    url: Optional[str] = Field(default=None, description="Optional URL for link-based checks.")
    notes: Optional[str] = Field(default=None, max_length=2000)

class StartCheckRequest(BaseModel):
    candidate: Candidate
    subreddits: List[str] = Field(default_factory=list, description="Subreddits to scan (e.g., ['pics','funny']). Use ['all'] for global.")
    lookback_days: Optional[int] = Field(default=None, ge=1, le=3650)
    min_title_similarity: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class StartCheckResponse(BaseModel):
    job_id: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    subreddits: List[str]
    lookback_days: int
    min_title_similarity: float
    started_at: str
    finished_at: Optional[str] = None
    candidate_path: str
    result_path: str

class ResultsResponse(BaseModel):
    job_id: str
    status: str
    candidate: Dict[str, Any]
    results: List[Dict[str, Any]]
    draft: Dict[str, Any]
