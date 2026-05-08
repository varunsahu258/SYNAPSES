"""Simple async load-testing utility for SYNAPSES API endpoints."""

from __future__ import annotations

import argparse
import asyncio
import time
from dataclasses import dataclass

import aiohttp


@dataclass(slots=True)
class LoadTestResult:
    total_requests: int
    succeeded: int
    failed: int
    duration_seconds: float


async def _worker(session: aiohttp.ClientSession, url: str, requests: int) -> tuple[int, int]:
    ok = 0
    fail = 0
    for _ in range(requests):
        try:
            async with session.get(url, timeout=5) as response:
                if response.status < 500:
                    ok += 1
                else:
                    fail += 1
        except (aiohttp.ClientError, asyncio.TimeoutError):
            fail += 1
    return ok, fail


async def run_load_test(url: str, concurrency: int, requests_per_worker: int) -> LoadTestResult:
    start = time.perf_counter()
    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        jobs = [_worker(session, url, requests_per_worker) for _ in range(concurrency)]
        results = await asyncio.gather(*jobs)
    succeeded = sum(ok for ok, _ in results)
    failed = sum(fail for _, fail in results)
    total = succeeded + failed
    return LoadTestResult(total, succeeded, failed, time.perf_counter() - start)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run basic API load test")
    parser.add_argument("--url", required=True)
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--requests-per-worker", type=int, default=100)
    args = parser.parse_args()

    result = asyncio.run(run_load_test(args.url, args.concurrency, args.requests_per_worker))
    rps = result.total_requests / result.duration_seconds if result.duration_seconds else 0.0
    print(
        f"total={result.total_requests} succeeded={result.succeeded} "
        f"failed={result.failed} duration={result.duration_seconds:.2f}s rps={rps:.2f}"
    )


if __name__ == "__main__":
    main()
