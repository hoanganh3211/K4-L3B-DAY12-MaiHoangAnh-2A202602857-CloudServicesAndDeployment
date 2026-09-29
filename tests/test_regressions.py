"""Additional checks for concurrency and configuration edge cases."""
from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException
import pytest


def test_concurrent_requests_cannot_share_last_quota(fake_redis):
    from app.rate_limiter import RateLimiter

    limiter = RateLimiter(fake_redis, 3)

    def hit(_):
        try:
            limiter.check("parallel", now=1000)
            return 200
        except HTTPException as exc:
            return exc.status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        statuses = list(pool.map(hit, range(20)))
    assert statuses.count(200) == 3
    assert statuses.count(429) == 17


def test_exact_budget_is_exhausted(fake_redis):
    from app.cost_guard import CostGuard

    guard = CostGuard(fake_redis, 1)
    guard.record("u1", 1)
    with pytest.raises(HTTPException) as error:
        guard.check("u1")
    assert error.value.status_code == 402


def test_repeated_signal_install_does_not_recurse():
    import signal
    from app.lifecycle import Lifecycle

    previous = {sig: signal.getsignal(sig) for sig in (signal.SIGTERM, signal.SIGINT)}
    try:
        calls = []
        signal.signal(signal.SIGTERM, lambda *args: calls.append(True))
        life = Lifecycle()
        life.install()
        life.install()
        life.request_shutdown(signal.SIGTERM)
        assert calls == [True]
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)
