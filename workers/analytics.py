import asyncio
import json
import time
from collections import defaultdict
from typing import Any
import redis.asyncio as aioredis


class AnalyticsAggregator:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._counters: dict[str, int] = defaultdict(int)
        self._timers: dict[str, list[float]] = defaultdict(list)

    async def connect(self):
        self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)

    async def close(self):
        await self.redis.aclose()

    # ── Counter operations ────────────────────────────────────────────────────

    async def increment(self, metric: str, value: int = 1, tags: dict | None = None):
        key = self._build_key(metric, tags)
        await self.redis.incrby(key, value)
        await self.redis.expire(key, 86400 * 30)  # 30 day TTL

    async def get_count(self, metric: str, tags: dict | None = None) -> int:
        key = self._build_key(metric, tags)
        val = await self.redis.get(key)
        return int(val or 0)

    # ── Time-series ───────────────────────────────────────────────────────────

    async def record_event(self, channel: str, event: dict):
        payload = json.dumps({**event, "ts": time.time()})
        await self.redis.xadd(f"stream:{channel}", {"data": payload}, maxlen=10_000)
        await self.redis.publish(f"channel:{channel}", payload)

    async def get_events(
        self,
        channel: str,
        count: int = 100,
        after: str = "-",
        before: str = "+",
    ) -> list[dict]:
        entries = await self.redis.xrange(f"stream:{channel}", after, before, count=count)
        return [json.loads(e[1]["data"]) for e in entries]

    # ── Rate tracking ─────────────────────────────────────────────────────────

    async def track_rate(self, metric: str, window_seconds: int = 60) -> float:
        now = time.time()
        key = f"rate:{metric}:{int(now // window_seconds)}"
        count = await self.redis.incr(key)
        await self.redis.expire(key, window_seconds * 2)
        return count / window_seconds

    # ── Histogram ─────────────────────────────────────────────────────────────

    async def record_duration(self, operation: str, duration_ms: float):
        key = f"hist:{operation}"
        await self.redis.zadd(key, {f"{time.time()}:{duration_ms}": duration_ms})
        await self.redis.zremrangebyscore(key, "-inf", time.time() - 3600)

    async def get_percentiles(self, operation: str) -> dict[str, float]:
        key = f"hist:{operation}"
        members = await self.redis.zrange(key, 0, -1, withscores=True)
        if not members:
            return {}
        values = sorted(s for _, s in members)
        n = len(values)
        return {
            "p50":  values[int(n * 0.50)],
            "p90":  values[int(n * 0.90)],
            "p95":  values[int(n * 0.95)],
            "p99":  values[int(n * 0.99)],
            "min":  values[0],
            "max":  values[-1],
            "mean": sum(values) / n,
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_key(self, metric: str, tags: dict | None) -> str:
        base = f"metric:{metric}"
        if not tags:
            return base
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{base}:{{{tag_str}}}"
