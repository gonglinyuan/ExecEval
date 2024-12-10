import logging
import multiprocessing as mp
import os

gunicorn_logger = logging.getLogger("gunicorn.error")

id_queue: mp.Queue | None = None


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
    global id_queue
    id_queue = mp.Manager().Queue()
    for i in range(int(os.environ["NUM_WORKERS"])):
        id_queue.put(i)


def pre_fork(server, worker):
    pass


def post_fork(server, worker):
    pass


def post_worker_init(worker):
    global id_queue
    app = worker.app.wsgi()
    app.init_engine(id_queue.get())
