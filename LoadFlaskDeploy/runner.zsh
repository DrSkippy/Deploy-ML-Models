echo "Starting and experiment..."

fn=2023-02-15_test
sleeptime=601

nohup poetry run python bin/client.py > ./data/${fn}1.csv &

echo "Sleeping for 10 m"
sleep $sleeptime

echo "Starting a new process..."
nohup poetry run python bin/client.py > ./data/${fn}2.csv &

echo "Sleeping for 10 m"
sleep $sleeptime

echo "Starting a new process..."
nohup poetry run python bin/client.py > ./data/${fn}3.csv &

echo "Sleeping for 10 m"
sleep $sleeptime

echo "Starting a new process..."
nohup poetry run python bin/client.py > ./data/${fn}4.csv &

echo "Sleeping for 10 m"
sleep $sleeptime

echo "Starting a new process..."
poetry run python bin/client.py > ./data/${fn}5.csv

cat ./data/${fn}*.csv | sort > ./data/consolidated_client.csv
cat ./data/consolidated_client.csv | cut -f 1 -d, | sort | uniq > ./data/pods.csv

echo "Done!"
