import time
from datetime import datetime

import numpy as np
import pandas as pd

import requests

promscale_endpoint = "http://192.168.127.7/prom"
promscale_query_url = f"{promscale_endpoint}/api/v1/query"

q_tags = '{image="localhost:32000/load-model-service:latest", pod=~"load-model-service-.*"}'
q_duration = '[{time_span}m:1m]'
pod_metric_types = ["cpu", "memory"]

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
        res[key] = pd.DataFrame(values, columns=["timestamp", "value"])
    return res

def experiment_pod_data_query(time_span=200):
    q_dur = q_duration.format(time_span=time_span)
    q_dict = {
        "cpu": f'rate(container_cpu_usage_seconds_total{q_tags}[1m]){q_dur}',
        "memory": f'rate(container_memory_usage_bytes{q_tags}[1m]){q_dur}'
    }
    assert(sorted(list(q_dict.keys())) ==  sorted(pod_metric_types))
    return q_dict

def fetch_experiment_pod_data(time_span=200):
    qlist = experiment_pod_data_query(time_span)
    res = {}
    for metric_type, query in qlist.items():
        # {metric_type: { pod: timeseries, ...}}
        res[metric_type] = prometheus_vector_series(query_prometheus(query))
    return res