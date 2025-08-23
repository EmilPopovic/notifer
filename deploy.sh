#!/bin/bash

set -e

REPO_BASE_URL="https://raw.githubusercontent.com/EmilPopovic/NotiFER/refs/heads/master"

echo "Creating deployment directory..."
mkdir -p notifer
cd notifer

echo "Creating database backup directory..."
mkdir db_backups

echo "Downloading compose file..."
curl -sL $REPO_BASE_URL/compose.yaml -o compose.yaml

echo "Creating directory structure..."
mkdir -p config
mkdir -p monitoring/{prometheus,grafana/provisioning/{dashboards,datasources},alertmanager}
mkdir -p db_backups

echo "Downloading configuration files..."
curl -sL $REPO_BASE_URL/config/app.conf -o config/app.conf

curl -sL $REPO_BASE_URL/monitoring/prometheus/prometheus.yml -o monitoring/prometheus/prometheus.yml
curl -sL $REPO_BASE_URL/monitoring/prometheus/alert_rules.yml -o monitoring/prometheus/alert_rules.yml
curl -sL $REPO_BASE_URL/monitoring/alertmanager/alertmanager.yml -o monitoring/alertmanager/alertmanager.yml
curl -sL $REPO_BASE_URL/monitoring/grafana/provisioning/dashboards/dashboards.yml -o monitoring/grafana/provisioning/dashboards/dashboards.yml
curl -sL $REPO_BASE_URL/monitoring/grafana/provisioning/dashboards/notifer-dashboard.json -o monitoring/grafana/provisioning/dashboards/notifer-dashboard.json
curl -sL $REPO_BASE_URL/monitoring/grafana/provisioning/datasources/prometheus.yml -o monitoring/grafana/provisioning/datasources/prometheus.yml

if [ ! -f .env ]; then
    echo "Creating .env template..."
    cat > .env << 'EOF'
# If using Resend to send emails, enter your API key
RESEND_API_KEY=

# If using SMTP to send emails, enter the server and port (i.e. smtp.google.com if using gmail)
SMTP_SERVER=
SMTP_PORT=587

# Email credentials for the email account used for sending confirmation emails
# Enter Resend info if using Resend and SMTP info if using SMTP
RESEND_CONFIRMATION_USERNAME=
SMTP_CONFIRMATION_USERNAME=
SMTP_CONFIRMATION_PASSWORD=

# Same as above but for notification emails
RESEND_UPDATE_USERNAME=
SMTP_UPDATE_USERNAME=
SMTP_UPDATE_PASSWORD=

# The password of the postgres database, username is postgres
POSTGRES_PASSWORD=

# MinIO password, also used to log in to the admin interface of MinIO, username is admin
S3_PASSWORD=

# Key used for generating tokens, make this long and random
JWT_KEY=

# Password of the Grafana metrics dashboard, username is admin
GRAFANA_PASSWORD=

# sha256 digest of API token used for privileged requests
# generate using `echo -n "your-secret-token"` | sha256sum
NOTIFER_API_TOKEN_HASH=

# Base URL of the API, i.e. https://notifer.example.com
API_URL=

# DO NOT CHANGE THESE VALUES
API_PORT=8026
MINIO_API_PORT=9002
MINIO_CONSOLE_PORT=9001
EOF
    echo "Please edit .env file with your passwords before running 'docker compose up -d'"
else
    echo ".env already exists, skipping..."
fi

echo "Deployment files ready! Edit .env then run: docker compose up -d"
