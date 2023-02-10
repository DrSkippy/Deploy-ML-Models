import numpy as np
import pandas as pd
import time
from datetime import datetime

import requests


promscale_endpoint = "http://192.168.127.7/prom"
promscale_query_url = f"{promscale_endpoint}/api/v1/query"

def query_prometheus(query: str, at: int = None):
    if at is None:
        at = int(time.time())
    response = requests.post(promscale_query_url, data={'query': query, 'time': at})
    return response.json()

def prometheus_vector_series(response_dict):
    res = {}
    for metric_dict in response_dict["data"]["result"]:
        key = metric_dict["metric"]["pod"]
        values = np.array(metric_dict["values"], dtype=np.float64)
        print(values, values.shape)
        res[key] = pd.DataFrame(values, columns=["timestamp", "value"])
    return res

def build_prometheus_plain_metric(name: str, value: float, labels: dict[str, str], type: str = "gauge", at: int = None):
    metric = f'# TYPE {name} {type}\n{name}'
    if len(labels) > 0:
        merged_labels = ','.join(f'{label_name}="{label_value}"' for label_name, label_value in labels.items())
        metric += f'{{{merged_labels}}}'
    metric += f' {value}'
    if at is not None:
        metric += f' {at}'
    return metric