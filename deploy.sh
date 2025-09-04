#!/bin/bash

set -e

REPO_BASE_URL="https://raw.githubusercontent.com/EmilPopovic/notifer/refs/heads/master"

echo "Creating deployment directory..."
mkdir -p notifer
cd notifer

echo "Downloading compose file..."
curl -sL $REPO_BASE_URL/compose.yaml -o compose.yaml

echo "Creating directory structure..."
mkdir -p config

echo "Downloading configuration files..."
curl -sL $REPO_BASE_URL/config/app.conf -o config/app.conf

if [ ! -f .env ]; then
    echo "Creating .env template..."
    cat > .env << 'EOF'
# If using Resend to send emails, enter your API key
RESEND_API_KEY=

# If using SMTP to send emails, enter the server and port (i.e. smtp.google.com if using gmail)
SMTP_SERVER=
SMTP_PORT=

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

# Key used for generating tokens, make this long and random
JWT_KEY=

# sha256 digest of API token used for privileged requests
# generate using `echo -n "your-secret-token"` | sha256sum
NOTIFER_API_TOKEN_HASH=

# Base URL of the API, i.e. https://notifer.example.com
API_URL=
EOF
    echo "Please edit .env file with your passwords before running 'docker compose up -d'"
else
    echo ".env already exists, skipping..."
fi

echo "Deployment files ready! Edit .env then run: docker compose up -d"
