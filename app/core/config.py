import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    # Reddit API (read-only usage supported; authentication optional but recommended for higher limits)
    REDDIT_CLIENT_ID: str = Field(default_factory=lambda: os.getenv("REDDIT_CLIENT_ID", ""))
    REDDIT_CLIENT_SECRET: str = Field(default_factory=lambda: os.getenv("REDDIT_CLIENT_SECRET", ""))
    REDDIT_USERNAME: str = Field(default_factory=lambda: os.getenv("REDDIT_USERNAME", ""))
    REDDIT_PASSWORD: str = Field(default_factory=lambda: os.getenv("REDDIT_PASSWORD", ""))
    REDDIT_USER_AGENT: str = Field(default_factory=lambda: os.getenv("REDDIT_USER_AGENT", "repost-assistant/1.0"))

    # Storage
    DATA_DIR: str = Field(default_factory=lambda: os.getenv("DATA_DIR", "data"))

    # Detection defaults
    DEFAULT_SUBREDDITS: str = Field(default_factory=lambda: os.getenv("DEFAULT_SUBREDDITS", "all"))  # comma-separated
    LOOKBACK_DAYS: int = Field(default_factory=lambda: int(os.getenv("LOOKBACK_DAYS", "90")))
    MAX_RESULTS_PER_QUERY: int = Field(default_factory=lambda: int(os.getenv("MAX_RESULTS_PER_QUERY", "50")))
    MIN_TITLE_SIMILARITY: float = Field(default_factory=lambda: float(os.getenv("MIN_TITLE_SIMILARITY", "0.78")))

    # Service controls
    MAX_ACTIVE_JOBS: int = Field(default_factory=lambda: int(os.getenv("MAX_ACTIVE_JOBS", "10")))

settings = Settings()
