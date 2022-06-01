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
