#!/bin/bash
PROJECT_DIR="/home/deploy/chipin-api"

set -e

echo "Starting deployment"

echo "Changing to project directory..."
cd "$PROJECT_DIR"

echo "Removing changes..."
git reset --hard HEAD

echo "Pulling latest changes..."
git pull

echo "Building and starting docker container..."
docker compose up -d --build

echo "Deployment completed"
