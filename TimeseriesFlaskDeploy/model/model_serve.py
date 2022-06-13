__version__ = '0.1.2'

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
      "model_id": "asd98f7a9s8df79ads",
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
    model_id = records["model_id"]
    m = load(file_path + model_id + ".pkl")
    if len(res) == 0:
        future = m.make_future_dataframe(periods=periods)
    forecast = m.predict(future)
    rdata = json.dumps({
        "size": forecast.shape,
        "data": forecast.to_numpy(),
        "header": forecast.columns,
        "model_id": model_id}
    }, cls = NumpyArrayEncoder)
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
    model_id = hash(str(records["size"]) + datetime.datetime.now())
    dump(m, filename=file_path + model_id + ".pkl")
    train_time = time.time() - start_time
    rdata = json.dumps({
        "size": records["size"],
        "training_time": train_time,
        "model_id": model_id})
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/validation/<model_id>')
def validation(model_id):
    """
    :return:
    """
    start_time = time.time()
    m = load(file_path + model_id + ".pkl")
    df_cv = cross_validation(m, initial='1095 days', period='365 days', horizon='180 days')
    df_p = performance_metrics(df_cv)
    train_time = time.time() - start_time
    rdata = json.dumps({"data": "XJSONX", "training_time": train_time, "model_id": model_id})
    rdata = rdata.replace('"XJSONX"', df_p.to_json())
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
