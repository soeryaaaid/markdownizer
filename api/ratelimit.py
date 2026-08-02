import asyncio
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


class InMemoryRateLimiter:
    def __init__(
        self,
        max_requests: int,
        window_seconds: float,
        prune_threshold: int = 10_000,
    ):
        self.max_requests = max_requests
        self.window = window_seconds
        self._prune_threshold = prune_threshold
        self._buckets: dict[str, deque[float]] = defaultdict(deque)
        self._last_seen: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def check_ip(self, request: Request) -> None:
        key = _client_ip(request)
        async with self._lock:
            now = time.monotonic()
            hits = self._buckets[key]
            while hits and hits[0] <= now - self.window:
                hits.popleft()
            if len(hits) >= self.max_requests:
                retry_after = int(max(1, self.window - (now - hits[0])))
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded, please retry later",
                    headers={"Retry-After": str(retry_after)},
                )
            hits.append(now)
            self._last_seen[key] = now
            if len(self._buckets) > self._prune_threshold:
                self._prune(now)

    def _prune(self, now: float) -> None:
        for key in [k for k in self._buckets if k in self._buckets]:
            if not self._buckets[key] and now - self._last_seen[key] > self.window:
                del self._buckets[key]
                del self._last_seen[key]