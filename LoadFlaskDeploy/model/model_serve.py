__version__ = '0.1.0'

from flask import Flask, Response, request, send_file
import json
import datetime
import time

import numpy as np
import pandas as pd

from joblib import load

from prometheus_flask_exporter.multiprocess import UWsgiPrometheusMetrics

# server configuration
from logging.config import dictConfig

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


class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyArrayEncoder, self).default(obj)


const_float = 0.346723846287346


def load(n=100, delay=0.001):
    for i in range(n):
        b = const_float * const_float
        time.sleep(delay)


def memory(size=100):
    a = np.array([size, size], dtype=float)


CALIBRATION_SCALE = 5000


def calibrate(n=10000):
    """
    Calculate the approximate load factor for translating time into multiplications
    """
    data = []
    a = 11
    for i in range(n):
        start_time = time.time()
        for j in range(CALIBRATION_SCALE):
            _ = a * a
        data.append(time.time() - start_time)
    return np.average(data)  # seconds per thousand


class Delay:
    """
    Delay class for generating random response times
    """

    def __init__(self,
                 endpoint="default",
                 conf=None,
                 **kwargs):
        self.endpoint = endpoint
        self.conf = conf
        self.data = kwargs
        # Todo, move outside and pass instantiated object for deterministic random sequence management
        self.delay_strategy = LogNormalDelayStrategy(self.conf.latency_mu, self.conf.latency_sigma)
        self.memory_strategy = NormalDelayStrategy(self.conf.memory_mu, self.conf.memory_sigma)

    def delayed_response(self):
        """
        Use class parameters to (1) delay for a random time and (2) package up a json
        payload describing the delay  and return a flask response.
        """
        if self.conf.latency_sigma == 0.0:
            t = self.conf.latency_mu
        else:
            t = self.delay_strategy()
        if random.random() < self.conf.latency_outlier_probability:
            # outlier is 6 sigma
            t += self.conf.latency_outlier_factor * self.conf.latency_sigma
        if self.conf.memory_sigma == 0.0:
            m = self.conf.memory_mu
        else:
            m = self.memory_strategy()
        if random.random() < self.conf.memory_outlier_probability:
            # outlier is 6 sigma
            m += self.conf.memory_outlier_factor * self.conf.memory_sigma
        at = self.load(t, m)
        self.data.update({
            "endpoint": self.endpoint,
            "params": {
                "latency": self.conf.mc("latency"),
                "memory": self.conf.mc("memory"),
                "load": self.conf.mc("load"),
                "delay": at}
        })
        rdata = json.dumps(self.data)
        response_headers = [
            ('Content-type', 'application/json'),
            ('Content-Length', str(len(rdata)))
        ]
        return Response(response=rdata, status=200, headers=response_headers)

    def load(self, t, m):
        """
        Time delay (seconds), processor load (1/0 thread), memory load (K bytes)...
        """
        block = np.ones((int(1024 * m / 4),), dtype=np.int32)
        at = t
        if self.conf.load_factor == 0:
            time.sleep(t)
        else:
            start_time = time.time()
            n = int(t * self.conf.load_calibration * CALIBRATION_SCALE)
            a = 11
            for j in range(n):
                _ = a * a
            at = time.time() - start_time
        del block
        return at


class LogNormalDelayStrategy:

    def __init__(self, mu, sigma, seed=None):
        np.random.seed(seed)
        mu2 = mu * mu
        sigma2 = sigma * sigma
        self.a = np.log(mu2 / np.sqrt(mu2 + sigma2))
        self.b = np.sqrt(np.log(1. + (sigma2 / mu2)))

    def __call__(self, size=1):
        """lognormal distributions"""
        if size == 1:
            # This value needs to be json serializable
            return float(np.random.lognormal(self.a, self.b, size=size)[0])
        else:
            # For generating a pre-deterministic list
            return np.random.lognormal(self.a, self.b, size=(size,))


class NormalDelayStrategy:

    def __init__(self, mu, sigma, seed=None):
        np.random.seed(seed)
        self.mu = mu
        self.sigma = sigma

    def __call__(self, size=1):
        """truncated normal distributions"""
        res = []
        for i in range(size):
            a = -1
            while a < 0:
                # return values must be positive
                a = float(np.random.normal(self.mu, self.sigma, size=size)[0])
            res.append(a)
        if size == 1:
            # This value needs to be json serializable
            return res[0]
        else:
            # For generating a pre-deterministic list
            return res


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


@app.route('/')
def main():
    call_result = {}
    result = Delay("/", conf=fsconf, calls=call_result).delayed_response()
    return result


@app.route('/metrics')
def metrics():
    """
    Creates the metrics endpoint for prometheus scrapes
    """
    from prometheus_client import multiprocess, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    response_headers = [
        ('Content-type', CONTENT_TYPE_LATEST),
        ('Content-Length', str(len(data)))
    ]
    return Response(response=data, status=200, headers=response_headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
