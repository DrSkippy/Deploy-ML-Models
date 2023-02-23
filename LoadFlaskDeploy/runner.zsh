echo "Starting and experiment..."
START="$(date +%s)"

ce="2023-02-20_5-replicas"
directory="./data/${ce}"
if [ ! -d ${directory} ]; then
  mkdir ${directory}
  echo "Created directory for experiment ${directory} ..."
else
  echo "Experiment already exists, not overwriting!"
  exit 1
fi

fn="2023-02-29_test"
sleeptime=400
PROCS=12

echo "Starting a new process 1 of ${PROCS} ..."
nohup poetry run python bin/client.py > ./data/${fn}1.csv &

for ((i = 2; i < $PROCS; i++)); do
  echo "Sleeping for ${sleeptime} seconds..."
  sleep $sleeptime

  echo "Starting a new process ${i} of ${PROCS} ..."
  nohup poetry run python bin/client.py > ./data/${fn}${i}.csv &
done

echo "Sleeping for ${sleeptime} seconds..."
sleep $sleeptime

echo "Starting a new process ${PROCS} of ${PROCS}..."
nohup poetry run python bin/client.py > ./data/${fn}${PROCS}.csv

cat ./data/${fn}*.csv | sort > ./data/consolidated_client.csv
echo "Total requests processed: $(wc -l ./data/consolidated_client.csv)"

cat ./data/consolidated_client.csv | cut -f 1 -d, | sort | uniq > ./data/pods.csv
echo "Number of replicas: $(wc -l ./data/pods.csv)"

DURATION=$[ $(date +%s) - ${START} ]

echo "Persisting prometheus data..."
poetry run python bin/persist_prometheus.py ${ce} ${DURATION}

echo "Moving outputs to experiment directory ${directory} ..."
mv ./data/*.csv ${directory}
mv ./data/*.json ${directory}

echo "Experiment ${ce} done in ${DURATION} seconds!"