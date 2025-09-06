"""RQ worker entrypoint for processing Phase Analyzer jobs."""

import os
from rq import Worker, Queue, Connection
import redis

listen = ["default"]
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")


def run_worker() -> None:
    conn = redis.from_url(redis_url)
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()


if __name__ == "__main__":
    run_worker()
