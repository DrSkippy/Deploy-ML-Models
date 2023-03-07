import datetime
import glob
import matplotlib.pyplot as plt
import os
import pandas as pd

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

field_names_std = [
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
    'response_load_calibration',
    'response_memory_request_std',
    'response_load_request_std'
]

field_names = field_names_std

base_data = "/Users/s.hendrickson/Working/Deploy-ML-Models/LoadFlaskDeploy/data"

all_experiments = [x for x in os.listdir(base_data) if "replicas" in x]

"""
find . -name '*test1.csv' | grep replicas  | xargs -I inf sh -c 'echo inf; head -n1 inf' | cut -d, -f8,12 \
       | paste -d " " - - | sort | sed 's/ /,/g'
"""
experiments_10_250 = [
    "2023-02-17_3-replicas",
    "2023-02-17_4-replicas",
    "2023-02-17_5-replicas",
    "2023-02-19_2-replicas",
    "2023-02-18_3-replicas",
    "2023-02-19_4-replicas",
    "2023-02-20_5-replicas",
    "2023-02-24_2-replicas",
    "2023-02-24_3-replicas",
    "2023-02-24_4-replicas",
    "2023-02-24_5-replicas",
    "2023-02-24_6-replicas",
    "2023-02-27_2-replicas",
    "2023-02-27_3-replicas",
    "2023-02-27_4-replicas",
    "2023-02-27_5-replicas",
    "2023-02-27_6-replicas",
    "2023-02-28_2-replicas",
    "2023-02-28_3-replicas",
    "2023-02-28_4-replicas"
]
experiments_10_350 = [
    "2023-02-26_2-replicas",
    "2023-02-26_3-replicas",
    "2023-02-26_4-replicas",
    "2023-02-26_5-replicas",
    "2023-02-26_6-replicas"
]

experiments_20_250 = [
    "2023-02-25_2-replicas",
    "2023-02-25_3-replicas",
    "2023-02-25_4-replicas",
    "2023-02-25_5-replicas",
    "2023-02-25_6-replicas"
]

client_data_file = "consolidated_client.csv"
pods_data_file = "pods.csv"


def persist_pod_dfs(dfs, experiment_name="tmp"):
    # dfs = {metric_type: { pod: time series, ...}}
    file_name_base = base_data + f'/{experiment_name}'
    if not os.path.exists(file_name_base):
        os.makedirs(file_name_base)
    file_name_base += f'/{datetime.datetime.utcnow().strftime("%Y-%m-%d_%H%M")}' + '_{}_{}.csv'
    for metric_type, df_dict in dfs.items():
        for pod_id, df in df_dict.items():
            file_name = file_name_base.format(metric_type, pod_id)
            df.to_csv(file_name, sep=',')


def plot_pod_metrics(dfs):
    for metric_type in dfs:
        pods_dict = dfs[metric_type]
        for pod_id, df in pods_dict.items():
            df.plot(y="value", title=f"pod={pod_id} type={metric_type}")


def extract_pod_id(fn):
    id = fn[-39:-4]
    return id


def extract_metric_type(fn):
    ty = fn[-43:-40]
    if ty == "cpu":
        return "cpu"
    elif ty == "ory":
        return "memory"
    else:
        print(f"WARNING: file name doesn't contain a valid metric_type! {fn} {ty}")


def read_pod_id_list(experiment_name):
    pod_ids = []
    with open(base_data + f'/{experiment_name}/{pods_data_file}') as infile:
        for x in infile:
            x = x.strip()
            if x is not None and x != "":
                pod_ids.append(x.strip())
    return pod_ids


def read_pod_df_list(experiment_name, tmin=None, tmax=None):
    file_name_pattern = base_data + f'/{experiment_name}/*load-model-service*'
    file_names = glob.glob(file_name_pattern)
    pod_ids = read_pod_id_list(experiment_name)
    res = {}
    for fn in file_names:
        pid = extract_pod_id(fn)
        pod_metric_type = extract_metric_type(fn)
        if pod_metric_type not in res:
            res[pod_metric_type] = {}
        if pid in pod_ids:
            with open(fn) as infile:
                _res = pd.read_csv(fn)
            if tmin is not None:
                _res = _res[_res['timestamp'] >= tmin]
            if tmax is not None:
                _res = _res[_res['timestamp'] <= tmax]
            _res["timestamp"] = _res["timestamp"].apply(lambda x: int(60 * int(x / 60.)))
            _res = _res.set_index("timestamp", drop=True)
            _res = _res.drop("Unnamed: 0", axis=1)
            res[pod_metric_type][pid] = _res
        else:
            print(f"WARNING: Pod id ({pid}) from data file not in pod list!")
    return res


def read_client_requests(experiment_name):
    data_file = base_data + f'/{experiment_name}/{client_data_file}'
    df = pd.read_csv(data_file, names=field_names)
    df_sorted = df.sort_values(by='response_start_time_sec')
    df_sorted["bucket_1_min"] = df_sorted["response_start_time_sec"].apply(lambda x: int(60 * int(x / 60.)))
    return df_sorted, df_sorted.response_start_time_sec.min(), df_sorted.response_start_time_sec.max()


def read_client_requests_in_progress():
    dfs = []
    file_name_pattern = base_data + '/*test*.csv'
    file_names = glob.glob(file_name_pattern)
    for data_file in file_names:
        dfs.append(pd.read_csv(data_file, names=field_names))
    df = pd.concat(dfs)
    return df.sort_values(by='response_start_time_sec')


def plot_client_latency_distribution(df, name, ax):
    print("=" * len(name))
    print(name)
    print("=" * len(name))
    print(df.client_latency_ms.describe())
    print()
    t = f'{name} ({df.shape[0]} reqs)'
    df.hist("client_latency_ms", bins=50, ax=ax)
    ax.set_title(t)
    ax.set_xlabel("client latency (ms)")


def compare_client_latency_distributions(experiments):
    fig, axs = plt.subplots(nrows=len(experiments), ncols=1, figsize=[8, 3 * len(experiments)])
    fig.tight_layout()
    for i, experiment in enumerate(experiments):
        df, _, _ = read_client_requests(experiment)
        plot_client_latency_distribution(df, experiment, axs[i])


def create_1_min_bucket_client_metrics(df):
    df_bucket = df.groupby('bucket_1_min').agg(
        request_rate_per_min=("bucket_1_min", "size"),
        avg_client_latency_ms=("client_latency_ms", "mean"),
        std_client_latency_ms=("client_latency_ms", "std"),
        avg_response_function_latency_ms=("response_function_latency_ms", "mean"),
        std_response_function_latency_ms=("response_function_latency_ms", "std"),
        avg_response_memory_usage_mb=("response_memory_usage_mb", "mean"),
        std_response_memory_usage_mb=("response_memory_usage_mb", "std"),
        avg_response_load_time_ms=("response_load_time_ms", "mean"),
        std_response_load_time_ms=("response_load_time_ms", "std")
    )
    df_bucket = df_bucket.reset_index()
    df_bucket.set_index("bucket_1_min", inplace=True)
    return df_bucket


def combined_data_set(current_experiment):
    df_client, first_request_time, final_request_time = read_client_requests(current_experiment)
    df_client = create_1_min_bucket_client_metrics(df_client)
    first_request_time = int(first_request_time)
    final_request_time = int(final_request_time + 120)

    df_pod = read_pod_df_list(current_experiment, first_request_time, final_request_time)
    df_mem = pd.concat(df_pod["memory"].values())
    df_mem = df_mem.groupby(level="timestamp").mean()
    df_cpu = pd.concat(df_pod["cpu"].values())
    df_cpu = df_cpu.groupby(level="timestamp").mean()
    df = df_mem.join(df_cpu, lsuffix="x")
    df.columns = ["memory", "cpu"]

    df = df.join(df_client)
    df["replicas"] = len(read_pod_id_list(current_experiment))
    return df

def combined_data_sets(experiments):
    dfs = [combined_data_set(ce) for ce in experiments]
    df = pd.concat(dfs, axis=0)
    df = df.dropna()
    return df