#!/bin/bash

set -e

RESOURCE_GROUP=""
APP_NAME=""
REGISTRY_NAME=""
LOCATION="eastus"

while [[ $# -gt 0 ]]; do
  case $1 in
    --resource-group) RESOURCE_GROUP="$2"; shift 2;;
    --app-name) APP_NAME="$2"; shift 2;;
    --registry-name) REGISTRY_NAME="$2"; shift 2;;
    --location) LOCATION="$2"; shift 2;;
    *) echo "Unknown option: $1"; exit 1;;
  esac
done

if [ -z "$RESOURCE_GROUP" ] || [ -z "$APP_NAME" ] || [ -z "$REGISTRY_NAME" ]; then
  echo "Usage: $0 --resource-group <rg> --app-name <app> --registry-name <registry> [--location <location>]"
  exit 1
fi

echo "Building Docker image..."
docker build -t "$REGISTRY_NAME.azurecr.io/movie-recommender:latest" Backend/

echo "Logging in to Azure Container Registry..."
az acr login --name "$REGISTRY_NAME"

echo "Pushing Docker image..."
docker push "$REGISTRY_NAME.azurecr.io/movie-recommender:latest"

echo "Deploying to Azure App Service..."
az webapp create \
  --resource-group "$RESOURCE_GROUP" \
  --plan "$APP_NAME-plan" \
  --name "$APP_NAME" \
  --deployment-container-image-name "$REGISTRY_NAME.azurecr.io/movie-recommender:latest"

echo "Configuring deployment..."
az webapp config container set \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --docker-custom-image-name "$REGISTRY_NAME.azurecr.io/movie-recommender:latest" \
  --docker-registry-server-url "https://$REGISTRY_NAME.azurecr.io"

echo "Deployment completed successfully"
