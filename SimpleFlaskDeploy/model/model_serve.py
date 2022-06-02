__version__ = '0.1.0'

from flask import Flask, Response, request, send_file
import json
import datetime

import numpy as np
import pandas as pd

from joblib import load

import training_data
import tensorflow as tf

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
def configuration():
    rdata = json.dumps({
        "version": __version__,
        "date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")})
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/predict', methods=['POST'])
def predict():
    """
    JSON Post Payload:
    { "size": 2,
      "data": [
            ['age', 'fnlwgt', 'sex-val', 'education-num', "capital-gain", "capital-loss", "hours-per-week"],
            ['age', 'fnlwgt', 'sex-val', 'education-num', "capital-gain", "capital-loss", "hours-per-week"]
        ]
    }
    :return:
    """
    records = request.get_json()
    df = pd.DataFrame(records["data"], columns=training_data.features)
    model_nn_sc = load("../data/neural_net_scaler.pkl")
    model_nn = load("../data/neural_net.pkl")
    data = model_nn_sc.transform(df)
    y_pred = model_nn.predict(data)
    rdata = json.dumps({"size": len(y_pred), "data": [np.argmin(x) for x in y_pred]}, cls=NumpyArrayEncoder)
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/example')
@app.route('/examples/<n>')
def examples(n=1):
    n = int(n)
    assert (n > 0)
    data = training_data.random_feature_sample_array(n)
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
