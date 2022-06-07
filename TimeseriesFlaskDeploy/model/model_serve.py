__version__ = '0.1.0'

from flask import Flask, Response, request, send_file
import json
import datetime

import numpy as np
import pandas as pd

from joblib import dump, load
from prophet import Prophet

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
    res = records["data"]
    periods = int(records["size"])
    m = load("../data/model.pkl")
    if len(res) == 0:
        future = m.make_future_dataframe(periods=periods)
    forecast = m.predict(future)
    res = forecast.to_numpy()
    header = forecast.columns
    rdata = {
        "size": res.shape,
        "data": res,
        "header": header
    }
    if len(res["errors"]) > 0:
        rdata = json.dumps(res, cls=NumpyArrayEncoder)
    else:
        df = pd.DataFrame(records["data"], columns=training_data.features)
        model_nn_sc = load("../data/neural_net_scaler.pkl")
        data = model_nn_sc.transform(df)
        y_pred = model_nn.predict(data)
        rdata = json.dumps({"size": len(y_pred), "data": [np.argmin(x) for x in y_pred]}, cls=NumpyArrayEncoder)
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/train', methods=['POST'])
def examples():
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
    records = request.get_json()
    periods = int(records["size"])
    data = np.array(records["data"])
    df = pd.DataFrame(data, columns=['ds', 'y'])
    m = Prophet()
    m.fit(df)
    m = dump("../data/model.pkl")
    res = {
        "size": n,
        "data": data
    }
    rdata = json.dumps(res, cls=NumpyArrayEncoder)
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
