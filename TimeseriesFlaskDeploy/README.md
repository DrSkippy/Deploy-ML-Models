


### Insalling tensorflow with poetry

microk8s.kubectl apply -f deployment.yaml 
microk8s.kubectl apply -f ingress.yml
microk8s.kubectl expose deployment ts-model-service --type=LoadBalancer --port=8085
microk8s.kubectl delete -f ingress.yml
microk8s.kubectl describe  deployment
microk8s.kubectl get services
microk8s.kubectl get ingress
microk8s.kubectl describe ingress
microk8s.kubectl rollout restart deployment/book-service


When using poetry, in your pyproject.toml edit manually (or whatever your version is):

[tool.poetry.dependencies]
python = ">=3.10,<3.11"
