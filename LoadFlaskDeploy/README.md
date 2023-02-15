




Local, no Docker (localhost, port 5000)

```
poetry run python model/model_serve.py
```

Local, Docker (localhost, port 5000)

```
docker build -t load_server .
docker run --detach -p 127.0.0.1:80:8080 load_server
docker stats --no-trunc <id of load server> 
```

K8S Deploy

```yaml
docker build -t localhost:32000/load-model-service .
docker push localhost:32000/load-model-service
microk8s.kubectl apply -f deployment.yaml
microk8s.kubectl expose deployment load-model-service --type=LoadBalancer --port=8080
kubectl rollout restart deployment/load-model-service
```

Change Replica Count
```yaml
microk8s.kubectl scale --replicas=4 deployment load-model-service 
```

Client

```yaml
poetry run python bin/client.py
```


Prometheus

```yaml
http://192.168.127.7/prom/graph
rate(container_cpu_usage_seconds_total{container="model-service"}[1m])
container_memory_usage_bytes{container="model-service"}

```