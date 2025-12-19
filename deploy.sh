#!/bin/bash

set -e

REPO_BASE_URL="https://raw.githubusercontent.com/EmilPopovic/notifer/refs/heads/master"

echo "Creating deployment directory..."
mkdir -p notifer
cd notifer

echo "Downloading compose file..."
curl -sL $REPO_BASE_URL/compose.yaml -o compose.yaml

echo "Downloading Makefile..."
curl -sL $REPO_BASE_URL/Makefile -o Makefile

if [ ! -f .env]; then
    echo "Downloading .env template..."
    curl -sL $REPO_BASE_URL/.env.template -o .env
else
    echo ".env already exists, downloading new template..."
    curl -sL $REPO_BASE_URL/.env.template -o .env.template
    echo "New .env template in .env.template"
fi

echo "Deployment files ready! Edit .env then run: docker compose up -d (make start)"
