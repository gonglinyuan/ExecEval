import json
import logging
import os
from queue import Queue

from filelock import FileLock

gunicorn_logger = logging.getLogger("gunicorn.error")

id_queue: Queue[int] | None = None


def worker_abort(worker):
    if not hasattr(worker, "wsgi"):
        worker.wsgi = worker.app.wsgi()
    if hasattr(worker.wsgi, "config"):
        config = worker.wsgi.config
        if "execution_engine" in config:
            worker.wsgi.logger.info("Stopping execution_engine")
            config["execution_engine"].stop()


def worker_exit(server, worker):
    worker_abort(worker)


def when_ready(server):
    pass


def on_starting(server):
    with open(os.environ["WORKER_CFG_DB"], "w") as f:
        json.dump(list(range(int(os.environ["NUM_WORKERS"]))), f)


def pre_fork(server, worker):
    pass


def post_fork(server, worker):
    pass


def post_worker_init(worker):
    with FileLock(os.environ["WORKER_CFG_DB"] + ".lock"):
        with open(os.environ["WORKER_CFG_DB"], "r") as f:
            remaining_ids = json.load(f)
        worker_id = remaining_ids.pop(0)
        with open(os.environ["WORKER_CFG_DB"], "w") as f:
            json.dump(remaining_ids, f)

    app = worker.app.wsgi()
    app.init_engine(worker_id)
