__version__ = '0.1.0'

from flask import Flask, Response, request, send_file
import pandas as pd
import json
import numpy as np
from joblib import load
from model import training_data as td

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

model_nn = load("neural_net.pkl")
model_nn_sc = load("neural_net_scaler.pkl")


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
    response_headers = resp_header(rdata)
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/predict', methods=['POST'])
def predict():
    """
    JSON Post Payload:
    { "size": 2,
      "data": [[],
      ...
      []]
    }
    :return:
    """
    records = request.get_json()
    records = nnsc.transform(records)
    y_pred = model.predict(records)
    rdata = json.dumps({"size" = len(records), "data": y_pred}, cls = NumpyArrayEncoder)
    response_headers = [
        ('Content-type', 'application/json'),
        ('Content-Length', str(len(rdata)))
    ]
    return Response(response=rdata, status=200, headers=response_headers)


@app.route('/exmple')
@app.route('/exmples/<n>')
def summary_books_read_by_year(n=1):
    da = td.random_feature_sample_array(n)
    res = {
        "size" = n,
                 "data" = da
    }
    rdata = json.dumps(res, cls=NumpyArrayEncoder))
    response_headers = [
    ('Content-type', 'application/json'),
    ('Content-Length', str(len(rdata)))

]
return Response(response=rdata, status=200, headers=response_headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
