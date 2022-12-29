__version__ = '0.1.0'

import datetime
import json
import numpy as np
import psutil
import time
import uuid
from flask import Flask, Response, request, send_file
from joblib import load
# server configuration
from logging.config import dictConfig
from prometheus_flask_exporter.multiprocess import UWsgiPrometheusMetrics

import model_util as mu

ds = mu.DelayStrategy(200)  # const 200 ms sleep

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)


@app.route('/version')
def configuration():
    rdata = json.dumps({
        "version": __version__,
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")})
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/', methods=["POST"])
def main():
    """
    request parameters:
    {
        "memory_request": 1,
        "load_reqeust": 1
    }
    """
    start_time = time.time()  # seconds
    uid = str(uuid.uuid4())
    app.logger.info(f"request id={uid} at ts={start_time}")
    # get the request parameters and log them
    parameters = request.get_json()
    app.logger.info(parameters)
    # allocate memory
    mem_handle = mu.memory_function(parameters["memory_request"])
    app.logger.info(mem_handle.shape)
    # execute loading
    load_time_ms, n, calibration = mu.load_function(parameters["load_request"])
    # for fractional loading, sleep part of the time
    sleep_delay_ms = ds.sleep()
    # wrap up measurements
    memory_usage_mb = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
    end_time = time.time()  # seconds
    function_latency_ms = (end_time - start_time) * 1000.  # ms
    # create the response record
    response = {
        "uuid": uid,
        "start_time_sec": start_time,
        "function_latency_ms": function_latency_ms,
        "memory_request": parameters["memory_request"],
        "memory_usage_mb": memory_usage_mb,
        "sleep_delay_ms": sleep_delay_ms,
        "load_time_ms": load_time_ms,
        "load_request": n,
        "load_calibration": calibration
    }
    del mem_handle  # let GC know it is okay to drop this ref
    rdata = json.dumps({
        "version": __version__,
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "response": response})
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
