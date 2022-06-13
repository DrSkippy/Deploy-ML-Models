import csv
import json

import pandas as pd
import numpy as np

file_path = "../data/"
# file_path = "./data/"    # useful for some local testing
dfile = file_path + "example_wp_log_peyton_manning.csv"


def get_training_data():
    with open(dfile, "r") as infile:
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
