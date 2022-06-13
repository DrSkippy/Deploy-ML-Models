import csv
import json
import datetime
import os


import pandas as pd
import numpy as np

from joblib import dump, load
from hashlib import sha512

app_name = os.getenv("APP_NAME")
if app_name == "TS-MODEL":
    model_pickle_path = "/cache/model-storage/"      # path of outputs of training models
else:
    model_pickle_path = "../pickles/"  # path of outputs of training models

example_data_file_path = "../data/"  # relative to python package
data_filename = example_data_file_path + "example_wp_log_peyton_manning.csv"


def get_training_data():
    with open(data_filename, "r") as infile:
        rdr = csv.reader(infile)
        first = True
        data = []
        for r in rdr:
            if first:
                header = r
                first = False
            else:
                data.append(r)
        data = np.array(data)
        return data, header


def persist_model(model):
    _tmp_string = "time_series_model" + str(datetime.datetime.now())
    model_id = sha512(_tmp_string.encode("ascii", errors="ignore")).hexdigest()[:40]
    # save the model for later use
    dump(model, filename=model_pickle_path + model_id + ".pkl")
    return model_id


def get_model(model_id):
    model = load(model_pickle_path + model_id + ".pkl")
    return model


class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return str(obj)
        elif isinstance(obj, pd.Index):
            return list(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyArrayEncoder, self).default(obj)
