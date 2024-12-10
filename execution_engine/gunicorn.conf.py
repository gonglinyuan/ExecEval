import logging

gunicorn_logger = logging.getLogger("gunicorn.error")


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
    pass


def pre_fork(server, worker):
    pass


def post_fork(server, worker):
    pass


def post_worker_init(worker):
    app = worker.app.wsgi()
    app.init_engine(worker.id)
