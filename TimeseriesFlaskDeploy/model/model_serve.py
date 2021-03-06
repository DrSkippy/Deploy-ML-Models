__version__ = '0.2.1'

import time

from flask import Flask, Response, request
from logging.config import dictConfig

from prophet import Prophet
from prophet.diagnostics import performance_metrics
from prophet.diagnostics import cross_validation

# data management utilities
from training_data import *

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
    :return: {'size': [2905, 2], 'training_time': 1.189, 'model_id': 'd61743627c2fb7f55fe1f7544ef887ced5e7141e'}
    """
    records = request.get_json()  # get the input parameters
    periods = int(records["size"][0])
    assert (periods > 0)  # much too forgiving!
    vector_length = int(records["size"][1])
    assert (vector_length == 2)
    data = np.array(records["data"])
    # TODO:
    # Train should save a data sample from training if
    # we want the example endpoint to work in the context of
    # specific model?
    start_time = time.time()  # Time training and log it
    # create training data frame
    df = pd.DataFrame(data, columns=['ds', 'y'])
    m = Prophet()  # model
    m.fit(df)  # model fit
    train_time = time.time() - start_time
    # keep track of the id of the model that we fit so the correct model is used
    # for validation and predictions!
    model_id = persist_model(m)
    rdata = json.dumps({
        "size": records["size"],
        "training_time": round(train_time, 3),
        "model_id": model_id})
    app.logger.info(f"model_server version = {__version__} model_id = {model_id} trained in {train_time} sec")
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
    m = get_model(model_id)
    if len(res) == 0:
        future = m.make_future_dataframe(periods=periods)
    forecast = m.predict(future)
    rdata = json.dumps({
        "size": forecast.shape,
        "data": forecast.to_numpy(),
        "header": forecast.columns,
        "model_id": model_id
    }, cls=NumpyArrayEncoder)
    app.logger.info(f"model_server version = {__version__} model_id = {model_id} predicted {periods} periods")
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
    m = get_model(model_id)
    start_time = time.time()
    df_cv = cross_validation(m, initial='2090 days', period='365 days', horizon='365 days')
    df_p = performance_metrics(df_cv)
    train_time = time.time() - start_time
    rdata = json.dumps({"data": "XJSONX", "training_time": train_time, "model_id": model_id})
    rdata = rdata.replace('"XJSONX"', df_p.to_json())
    app.logger.info(f"model_server version = {__version__} model_id = {model_id} cross-validation in {train_time} s")
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
