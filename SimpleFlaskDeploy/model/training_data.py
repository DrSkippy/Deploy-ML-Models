import pandas as pd
import numpy as np

file_path = "../data/adult_earning/"
hfile = file_path + "adult.names"
dfile = file_path + "adult.data"

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
    features = ['age', 'fnlwgt', 'sex-val', 'education-num', "capital-gain", "capital-loss", "hours-per-week"]
    df = get_training_dataframe()
    df["sex-val"] = df["sex"].apply(lambda x: 1 if "M" in x else 0)
    return df[features].copy()

def random_feature_sample(n=1):
    df = select_encoded_features()
    df.sample(n)
    return df

def random_feature_sample_array(n=1):
    df = random_feature_sample(n)
    return df.to_numpy(copy=True)


