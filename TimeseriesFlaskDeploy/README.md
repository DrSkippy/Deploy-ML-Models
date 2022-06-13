


### Deploying to K8s

microk8s.kubectl apply -f deployment.yaml 
microk8s.kubectl apply -f ingress.yml
microk8s.kubectl expose deployment ts-model-service --type=LoadBalancer --port=8085
microk8s.kubectl delete -f ingress.yml
microk8s.kubectl describe  deployment
microk8s.kubectl get services
microk8s.kubectl get ingress
microk8s.kubectl describe ingress
microk8s.kubectl rollout restart deployment/book-service

docker build -t localhost:32000/ts-model-service .
docker push localhost:32000/ts-model-service
microk8s.kubectl rollout restart deployment/ts-model-service

