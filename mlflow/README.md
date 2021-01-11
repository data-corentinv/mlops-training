docker build --rm -f "Dockerfile" -t mlflow-group-1:latest .
docker tag mlflow-group-1:latest eu.gcr.io/yotta-mlops/mlflow-group-1:latest
docker push eu.gcr.io/yotta-mlops/mlflow-group-1:latest

kubectl apply -f deployment.yml
kubectl exec -it mlflow-group-1-86b87f5f8b-l6hdc --container mlflow -- /bin/bash
kubectl apply -f service.yml
kubectl get pods
kubectl logs mlflow-group-1-86b87f5f8b-l6hdc --container mlflow



kubectl exec -it mlflow-group-1-867bfc4759-z4l8q -- /bin/bash
dans le service colibrimmo 
```
export MLFLOW_TRACKING_URI=http://34.77.161.208:5000
export GOOGLE_APPLICATION_CREDENTIALS=conf/local/service_account.json