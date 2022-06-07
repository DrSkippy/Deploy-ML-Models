import csv

import pandas as pd
import numpy as np

file_path = "../data/"
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
