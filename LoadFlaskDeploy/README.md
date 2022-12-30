




Local, no Docker (localhost, port 5000)

```
poetry run python model/model_serve.py
```

Local, Docker (localhost, port 5000)

```
docker build -t load_server .
docker run --detach -p 127.0.0.1:80:8080 load_server
docker stats --no-trunc <container id>
```


Client

```yaml
poetry run python bin/client.py
```