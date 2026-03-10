#!/bin/bash

set -e

RESOURCE_GROUP=""
REGISTRY_NAME=""
LOCATION="eastus"

while [[ $# -gt 0 ]]; do
  case $1 in
    --resource-group) RESOURCE_GROUP="$2"; shift 2;;
    --registry-name) REGISTRY_NAME="$2"; shift 2;;
    --location) LOCATION="$2"; shift 2;;
    *) echo "Unknown option: $1"; exit 1;;
  esac
done

if [ -z "$RESOURCE_GROUP" ] || [ -z "$REGISTRY_NAME" ]; then
  echo "Usage: $0 --resource-group <rg> --registry-name <registry> [--location <location>]"
  exit 1
fi

echo "Creating resource group..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION"

echo "Creating Azure Container Registry..."
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$REGISTRY_NAME" \
  --sku Basic \
  --admin-enabled true

echo "Registry setup completed"
echo "Registry URL: $REGISTRY_NAME.azurecr.io"
