


### Deploying to K8s

```
microk8s.kubectl apply -f deployment.yaml 
microk8s.kubectl apply -f ingress.yml
microk8s.kubectl expose deployment ts-model-service --type=LoadBalancer --port=8085
microk8s.kubectl delete -f ingress.yml
microk8s.kubectl describe  deployment
microk8s.kubectl get services
microk8s.kubectl get ingress
microk8s.kubectl describe ingress
```

Update and redeploye
```
docker build -t localhost:32000/ts-model-service .
docker push localhost:32000/ts-model-service
microk8s.kubectl rollout restart deployment/ts-model-service
```


### PVC

```
ubuntu@k8s-worker-04:/mnt/disk/vol1/Working/Deploy-ML-Models/TimeseriesFlaskDeploy$ microk8s.kubectl apply -f pvc.yaml 
persistentvolumeclaim/model-storage-claim created
ubuntu@k8s-worker-04:/mnt/disk/vol1/Working/Deploy-ML-Models/TimeseriesFlaskDeploy$ microk8s.kubectl get pvc
NAME                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS          AGE
test-claim            Bound    pvc-456464a4-c78c-4434-87d3-71614817e27c   1Mi        RWX            managed-nfs-storage   17d
model-storage-claim   Bound    pvc-d14725db-e16b-480f-9123-d664cca56659   10Mi       RWX            managed-nfs-storage   11s
```
