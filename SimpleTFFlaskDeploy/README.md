

### Build and deploy on k8s

```
docker build -t localhost:32000/earnings-model-server .
docker push localhost:32000/earnings-model-server
```

#### Dev Env

```angular2html
docker build -t earnings-model-server .
docker run -p 127.0.0.1:80:8080 earnings-model-server
```

### Installing tensorflow with poetry

When using poetry, in your pyproject.toml edit manually (or whatever your version is):

```
[tool.poetry.dependencies]
python = ">=3.10,<3.11"
```

#### Installing Tensorflow on Raspberry Pi

Isn't straight forward at all...

