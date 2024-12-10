import logging
import os
import sys
import time
import traceback
from pathlib import Path

from flask import Flask, request
from flask_cors import CORS

from config import load_config
from exec_outcome import ExecOutcome
from execution_engine import ExecutionEngine
from job import JobData

sys.path.extend([str(Path(__file__).parent)])

app = Flask(__name__)
CORS(app)

gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

execution_engine: ExecutionEngine | None = None


def init_engine(worker_id: int):
    global execution_engine
    config_path = Path("config.yaml")
    cfg = load_config(config_path)
    gid = int(os.environ["RUN_GID"]) + worker_id
    uid = int(os.environ["RUN_UID"]) + worker_id
    execution_engine = ExecutionEngine(cfg, (gid, uid), app.logger)
    app.config["execution_engine"] = execution_engine
    execution_engine.start()


@app.route("/api/execute_code", methods=["POST"])
def run_job():
    log, ret, st = "", None, time.perf_counter_ns()
    try:
        job = JobData.json_parser(request.json)
        log = f"api/execute_code: lang={job.language}"
        result = execution_engine.check_output_match(job)
        ret = {"data": [r.json() for r in result]}
        exec_outcomes = [
                            r.exec_outcome
                            for r in result
                            if not (r.exec_outcome is None or r.exec_outcome is ExecOutcome.PASSED)
                        ] + [ExecOutcome.PASSED]
        peak_mem = max([int(r.peak_memory_consumed.split()[0]) for r in result if r.peak_memory_consumed] + [-1])
        peak_time = max([r.time_consumed for r in result if r.time_consumed] + [-1])
        log = f"{log} time: {(time.perf_counter_ns() - st) / (1000_000_000)}s, |uts|={len(job.unittests)}, exec_outcome={exec_outcomes[0].value}, peak_mem={peak_mem}kB, peak_time={peak_time}s"

    except Exception as e:
        ret = {"error": str(e) + f"\n{traceback.print_exc()}"}, 400
        log = f"{log} time: {(time.perf_counter_ns() - st) / (1000_000_000)}s, {ret}"
    app.logger.info(log)
    return ret


@app.route("/api/all_runtimes", methods=["GET"])
def all_runtimes():
    log, st = "", time.perf_counter_ns()
    runtimes = []
    for runtime in execution_engine.supported_languages.values():
        runtimes.append(runtime.get_info())
    ret = runtimes, 200
    log = f"api/all_runtimes: {log} time: {(time.perf_counter_ns() - st) / (1000_000_000)}s"

    app.logger.info(log)
    return ret


if __name__ == "__main__":
    app.run(host="0.0.0.0")
