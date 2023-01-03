




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
```

Client

```yaml
poetry run python bin/client.py
```