__version__ = '0.1.0'

from flask import Flask, Response, request
import json
import datetime
import time

import numpy as np
import pandas as pd

from joblib import dump, load

from prophet import Prophet
from prophet.diagnostics import performance_metrics
from prophet.diagnostics import cross_validation

# data management utilities
from training_data import *

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


@app.route('/version')
def version():
    rdata = json.dumps({
        "version": __version__,
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")})
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/example')
def example():
    d, h = get_training_data()
    rdata = json.dumps({
        "size": d.shape,
        "data": d,
        "header": h}, cls=NumpyArrayEncoder)
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/predict', methods=['POST'])
def predict():
    """
    JSON Post Payload:
    { "size": 4,
      "data": [
            [datetime1],
            [datetime2],
            ...
        ]
    }
    :return:
    """
    records = request.get_json()
    res = np.array(records["data"])
    periods = int(records["size"])
    m = load(file_path + "model.pkl")
    if len(res) == 0:
        future = m.make_future_dataframe(periods=periods)
    forecast = m.predict(future)
    rdata = json.dumps({
        "size": forecast.shape,
        "data": forecast.to_numpy(),
        "header": forecast.columns
    }, cls=NumpyArrayEncoder)
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/train', methods=['POST'])
def train():
    """
    JSON Post Payload:
    { "size": 4,
      "data": [
            [datetime1, y1],
            [datetime2, y2],
            ...
        ]
    }
    :return:
    """
    start_time = time.time()
    records = request.get_json()
    periods = int(records["size"][0])
    vector_length = int(records["size"][1])
    assert (vector_length == 2)
    data = np.array(records["data"])
    df = pd.DataFrame(data, columns=['ds', 'y'])
    m = Prophet()
    m.fit(df)
    dump(m, filename=file_path + "model.pkl")
    train_time = time.time() - start_time
    rdata = json.dumps({"size": records["size"], "training_time": train_time})
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/validation')
def validation():
    """
    :return:
    """
    start_time = time.time()
    m = load(file_path + "model.pkl")
    df_cv = cross_validation(m, initial='730 days', period='365 days', horizon='365 days')
    df_p = performance_metrics(df_cv)
    train_time = time.time() - start_time
    rdata = json.dumps({"data": "XJSONX", "training_time": train_time})
    rdata = rdata.replace('"XJSONX"', df_p.to_json())
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
