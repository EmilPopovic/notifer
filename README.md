# NotiFER

[![Status](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus.notifer.emilpopovic.me%2Fshield-badges%2Fstatus.json&style=flat)](https://status.notifer.emilpopovic.me)
[![License](https://img.shields.io/github/license/EmilPopovic/notifer)](https://github.com/EmilPopovic/notifer/blob/master/LICENSE)
[![Release](https://img.shields.io/github/v/release/EmilPopovic/notifer)](https://github.com/EmilPopovic/notifer/releases)

**[NotiFER](https://notifer.emilpopovic.me/)** is a modern, open-source web application designed for students at [FER](https://www.fer.unizg.hr/en), University of Zagreb. It automatically monitors university calendars and sends timely email notifications about timetable changes, ensuring students never miss an update.

> [!NOTE]
> **NotiFER is not affiliated with FER.** It's creator is a student who wanted himself and his colleagues to have a useful tool.

## Key Features

- **Automatic Calendar Change Detection:**
    Monitors FER calendars and notifies students by email whenever a change is detected.

- **Easy Subscription:**
    Students simply paste their calendar URL to subscribe.

- **Secure & Privacy-Respecting:**
    No unnecessary data is collected. All sensitive operations are protected and GDPR-friendly. Calendar credentials are encrypted at rest in the database.

- **Internationalization:**
    Fully localized in Croatian and English.

- **Admin Dashboard:**
    A built-in web dashboard at `/dashboard/` lets administrators view subscription stats, manage users (pause/unpause/delete), and browse a full audit log of all actions.

- **Audit Logging:**
    Every significant action (subscription, activation, notification, deletion, etc.) is recorded to the database with a timestamp.

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

    If you have [Make](https://www.gnu.org/software/make/) on your system, run:

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
    [Official instructions](https://docs.docker.com/engine/install/)

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
    - `JWT_KEY` - secret key used for generating tokens (long random string)
    - `ENCRYPTION_KEY` - Fernet key for encrypting calendar credentials at rest; generate with:
        ```bash
        python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
        ```
    - `NOTIFER_API_TOKEN_HASH` - SHA-256 hash of the admin API token; generate with `echo -n "your-secret-token" | sha256sum`
    - `DASHBOARD_USERNAME` - username for the admin web dashboard (default: `admin`)
    - `DASHBOARD_PASSWORD_HASH` - hashed dashboard password; generate with:
        ```bash
        docker compose exec notifer python -c "from shared.auth_utils import hash_password; print(hash_password('yourpassword'))"
        ```
    - `API_URL` - the URL at which users will access the app (for example `https://notifer.emilpopovic.com`)

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

- Pre-built Docker image from [GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- PostgreSQL database

**Deployment structure:**

```bash
notifer/
├── compose.yaml          # Main deployment file
├── .env                  # Your configuration
└── Makefile              # Management actions
```

## Admin Dashboard

A password-protected web UI is available at `/dashboard/`. It provides:

- **Overview:** total and active subscription counts, total changes detected.
- **User management:** list all subscribers, pause/unpause/delete with confirmation.
- **Audit log:** paginated, filterable history of every action taken in the system.
- **Per-user view:** subscription details and the full action history for a specific user.

Credentials are configured via `DASHBOARD_USERNAME` and `DASHBOARD_PASSWORD_HASH` in `.env`.

## Admin API

The REST API at `/admin` allows programmatic management of subscriptions:

- Add or remove subscriptions.
- Pause or resume notifications for any user.
- Query subscription status and details.

All endpoints require a `Bearer` token matching `NOTIFER_API_TOKEN_HASH`.

## Security & Privacy

- **No unnecessary data collection.**
- **Calendar credentials are encrypted at rest** using Fernet (AES-128-CBC + HMAC-SHA256).
- **All sensitive actions require confirmation** via token-protected links and/or POST form submission (preventing email scanner prefetch attacks).
- **Full audit trail** — every action is logged with a timestamp to the database.
- **Open codebase for full transparency.**

## License

NotiFER is open source and available under the [MIT License](LICENSE)

## Contact

For questions, support, or a demo, please contact:
**Emil Popović**
<admin@emilpopovic.me>

_NotiFER is currently developed and maintained by Emil Popović, a student at FER._

