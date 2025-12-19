# NotiFER

[![Status](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus.notifer.emilpopovic.me%2Fshield-badges%2Fstatus.json&style=flat)](https://status.notifer.emilpopovic.me)
[![License](https://img.shields.io/github/license/EmilPopovic/notifer)](https://github.com/EmilPopovic/notifer/blob/master/LICENSE)
[![Release](https://img.shields.io/github/v/release/EmilPopovic/notifer)](https://github.com/EmilPopovic/notifer/releases)

**NotiFER** is a modern, open-source web application designed for students at FER, University of Zagreb. It automatically monitors university calendars and sends timely email notifications about timetable changes, ensuring students never miss an update.

## Key Features

- **Automatic Calendar Change Detection:**
    Monitors FER calendars and notifies students by email whenever a change is detected.

- **Easy Subscription:**
    Students simply paste their calendar URL to subscribe.

- **Secure & Privacy-Respecting:**
    No unecessary data is collected. All sensitive operations are protected and GDPR-friendly.

- **Internationalization:**
    Fully localized in Croatian and English.

- **Admin API:**
    Administrators can securely manage subscriptions (add, remove, pause, resume, query) via a protected API.

- **Self-Hosting Ready:**
    Easily deployable via Docker Compose.

## Why NotiFER?

- **Reliability:**
    Developed and maintained by a FER student, NotiFER has already detected hundreds of timetable changes and helped students stay up-to-date with their studies.

- **Open Source:**
    Anyone can freely review, audit, and contribute to the codebase.

## How It Works

1. **Sign Up:**
    Students visit the website and paste their FER calendar URL.
2. **Confirm Subscription:**
    A confirmation email is sent to their FER email address. They activate their subscription by clicking the magic link.
3. **Receive Notifications:**
    NotiFER monitors their calendar and sends an email notification whenever a change occurs.

## Hosting & Deployment

### Quick Start - From Source (Docker compose)

1. **Install Docker:**
    [Official instructions](https://docs.docker.com/engine/install/)

2. **Clone the repository:**

    ```bash
    git clone https://github.com/EmilPopovic/notifer.git
    cd notifer
    ```

3. **Configure environment:**

    Edit `.env.example`, then rename:

    ```bash
    mv .env.example .env

4. **Initialize the database:**

    If you have Make on your system, run:

    ```bash
    make initdb COMPOSE_FILE=compose.dev.yaml
    ```

    Otherwise, run:

    ```bash
    docker compose -f compose.dev.yaml run --build --rm notifer python -m src.db_manager create
    ```

5. **Run the service:**

    Again, there is a Make version and a no-Make version:

    ```bash
    make upd COMPOSE_FILE=compose.dev.yaml
    ```

    ```bash
    docker compose -f compose.dev.yaml up --build -d
    ```

6. **Set up a reverse proxy (optional):**
    The app runs on port `8026`.

### Quick Start - From Registry (Docker compose)

**This is the recommended deployment method for production environments.**

1. **Install Docker:**
    [Official Docker installation instructions](https://docs.docker.com/engine/install/)

2. **Download and run the deployment script:**

    ```bash
    curl -sL https://raw.githubusercontent.com/EmilPopovic/notifer/refs/heads/master/deploy.sh | bash
    ```

    Or manually download and execute:

    ```bash
    wget https://raw.githubusercontent.com/EmilPopovic/notifer/refs/heads/master/deploy.sh
    chmod +x deploy.sh
    ./deploy.sh
    ```

3. **Configure environment:**

    The script creates a `notifer/` directory with all necessary files. Edit the `.env` file:

    ```bash
    cd notifer
    nano .env  # or use your preferred editor
    ```

    **Required configuration:**
    - `SMTP_SERVER` - the server used for sending email
    - `SMTP_PORT` - SMTP port (usually `465` or `587`)
    - `SMTP_USERNAME`
    - `SMTP_SENDER_EMAIL` - the address in the "From" field
    - `SMTP_PASSWORD`
    - `POSTGRES_PASSWORD`
    - `JWT_KEY` - secret key used for generating tokens
    - `NOTIFER_API_TOKEN_HASH` - hash of the API token for the admin API, generate using `echo -n "your-secret-token" | sha256sum`
    - `API_URL` - the URL at which users will access the app (for example [https://notifer.emilpopovic.com](https://notifer.emilpopovic.com))

4. **Deploy:**

    ```bash
    # If you have Make
    make initdb
    make upd
    ```

    ```bash
    # If you do not have make
    docker compose run --rm notifer python -m src.db_manager create
    docker compose up -d
    ```

**What gets deployed:**

- Pre-built Docker image from GHCR
- PostgreSQL database

**Deployment structure:**

```bash
notifer/
├── compose.yaml          # Main deployment file
├── .env                  # Your configuration
└── Makefile              # Management actions
```

## Admin API

Administration can:

- Add or remove subscriptions via secure API endpoints.
- Pause or resume notifications for any user.
- Query subscription status and details.
- All actions require a secure API token (see documentation)

## Security & Privacy

- **No unecessary data collection.**
- **All sensitive actions require confirmation and/or secure API tokens.**
- **Open codebase for full transparency.**

## License

NotiFER is open source and available under the [MIT License](LICENSE)

## Contact

For questions, support, or a demo, please contact:
**Emil Popović**
<admin@emilpopovic.me>

_NotiFER is currently developed and maintained by Emil Popović, a student at FER._
