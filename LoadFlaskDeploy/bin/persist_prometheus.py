import sys

import notebook_libs.utilities as util
import notebook_libs.prometheus as prom

current_experiment = sys.argv[1].strip()
duration_min = int((float(sys.argv[2]) + 220.)/60.)  # 220 sec of padding

result = prom.fetch_experiment_pod_data(duration_min)
util.persist_pod_dfs(result, current_experiment)

print(f"Done persisting. current_experiment={current_experiment} duration={duration_min} minutes")