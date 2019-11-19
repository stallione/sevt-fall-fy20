#!/bin/bash

# Services
kubectl delete -f yaml/apiserver-service.yaml
kubectl delete -f yaml/frontend-service.yaml

# Deployments
kubectl delete -f yaml/weather-deployment.yaml
kubectl delete -f yaml/event-deployment.yaml
kubectl delete -f yaml/incident-deployment.yaml
kubectl delete -f yaml/apiserver-deployment.yaml
kubectl delete -f yaml/frontend-deployment.yaml
