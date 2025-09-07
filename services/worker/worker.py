import os

from rq import Connection, Worker
from redis import Redis


def main() -> None:
    """Run an RQ worker processing the 'default' queue."""
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    redis = Redis.from_url(redis_url)
    with Connection(redis):
        worker = Worker(["default"])
        worker.work()


if __name__ == "__main__":
    main()
