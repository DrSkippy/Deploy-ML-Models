import csv

import pandas as pd
import numpy as np

file_path = "../data/"
hfile = file_path + "adult.names"
dfile = file_path + "adult.data"
features = ['age', 'fnlwgt', 'sex-val', 'education-num', "capital-gain", "capital-loss", "hours-per-week"]
with open(file_path + "feature_vetting.csv", "r") as infile:
    rdr = csv.reader(infile)
    vetting = []
    vheader = True
    for line in rdr:
        if vheader:
            vkeys = {x: i for i, x in enumerate(line)}
            vheader = False
        else:
            vetting.append([line[0]] + [float(x) for x in line[1:]])


def get_header():
    header = []
    with open(hfile, "r") as infile:
        for line in infile:
            if line.startswith("|") or line.startswith(">") or line.startswith("\n"):
                continue
            else:
                header.append(line.split(":")[0])
    header.append("class")
    return header


def get_training_dataframe():
    header = get_header()
    df = pd.read_csv(dfile, names=header)
    return df


def select_encoded_features():
    df = get_training_dataframe()
    df["sex-val"] = df["sex"].apply(lambda x: 1 if "M" in x else 0)
    return df[features].copy()


def random_feature_sample(n=1):
    df = select_encoded_features()
    return df.sample(n)


def random_feature_sample_array(n=1):
    df = random_feature_sample(n)
    return df.to_numpy(copy=True)


def vet_features(data):
    """
    :param data: 2 dim np.array, row length must be equal to features in the model
    :return: dictionary of analysis results include size, list of errors and list of warnings
    """
    if isinstance(data, list):
        data = np.array(data)
    msgs = {"size": data.shape, "errors": [], "warnings": []}
    if len(data[0]) != len(features):
        msgs["errors"].append(f"Wrong number of features (got {len(data[0])} but should be {len(features)})")
        return msgs
    for vidx, vet_row in enumerate(vetting):
        if vidx == 0:
            continue
        # in order we should receive features
        for didx, data_row in enumerate(data):
            d = float(data_row[vidx])
            if d < vet_row[vkeys["min"]] or d > vet_row[vkeys["max"]]:
                _msg = (f"feature {vetting[vidx][0]} value ({d}) out of range "
                        f"[{vet_row[vkeys['min']]}, {vet_row[vkeys['max']]}] "
                        f"of training data in vector {didx}")
                mesg["errors"].append(_msg)
            if d < vet_row[vkeys["25%"]] or d > vet_row[vkeys["75%"]]:
                _msg = (f"feature {vetting[vidx][0]} value ({d}) out of quartile range "
                        f"[{vet_row[vkeys['25%']]}, {vet_row[vkeys['75%']]}] "
                        f"of training data in vector {didx}")
                msgs["warnings"].append(_msg)
    return msgs
