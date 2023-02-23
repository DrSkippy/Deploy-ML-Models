import requests
import time
import csv
import sys
import json
import uuid

import model.model_util as mu

ds = mu.NormalDelayStrategy(mu=700, sigma=300)  # const 200 ms sleep

input_parameters_template = {
    "memory_request": 250,
    "load_request": 10
}

n = 4000

def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        # If the Nested key-value
        # pair is of dict type
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        # If the Nested key-value
        # pair is of list type
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out


field_names = [
    'response_hostname',
    'client_latency_ms',
    'version', 'date',
    'response_uuid',
    'response_start_time_sec',
    'response_function_latency_ms',
    'response_memory_request',
    'response_memory_usage_mb',
    'response_sleep_delay_ms',
    'response_load_time_ms',
    'response_load_request',
    'response_load_calibration'
]

# url = "http://localhost:5000"
# url = "http://localhost"
url = "http://192.168.127.8/load-model/"

writer = csv.DictWriter(sys.stdout, fieldnames=field_names)
codes = {}
for i in range(n):
    start_time = time.time()
    r = requests.post(url, json=input_parameters_template)
    client_latency_ms = 1000. * (time.time() - start_time)
    if r.status_code >= 200 and r.status_code < 300:
        record = flatten_json(r.json())
        record["client_latency_ms"] = client_latency_ms
        writer.writerow(record)
    codes[r.status_code] = codes.get(r.status_code, 0) + 1
    _ = ds.sleep() # Use a random delay after request is processed to break
                   # resonances in request times when running multiple clients

with open(f"./data/{uuid.uuid4()}.json", "w") as ofile:
    json.dump(codes, ofile)
    ofile.write("\n")
