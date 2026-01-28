import time
from dataclasses import dataclass, field

@dataclass
class RateLimiter:
    """Simple pacing helper for API calls."""
    min_interval_seconds: float = 1.0
    _last_ts: float = field(default_factory=lambda: 0.0)

    def wait(self) -> None:
        now = time.time()
        elapsed = now - self._last_ts
        if elapsed < self.min_interval_seconds:
            time.sleep(self.min_interval_seconds - elapsed)
        self._last_ts = time.time()
