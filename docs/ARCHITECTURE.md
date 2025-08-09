# 🏗️ NotiFER System Architecture

NotiFER is designed as a modular, scalable, and secure notification platform for university calendar changes.
The system is composed of several cooperating components, each running in its own container for reliability and maintainability.

## Components

### 1. **API Service (`api/`)**

- **Framework:** FastAPI (Python)
- **Responsibilities:**
  - Exposes REST endpoints for student and university admin actions
  - Handles subscription management, confirmation, and API authentication
  - Servves the static frontend
  - Provides health and metrics endpoints
- **Deployment:** Runs as a Docker container

### 2. **Calendar Worker (`calendar_worker/`)**

- **Framework:** Python
- **Responsibilities:**
  - Periodically checks all active subscriptions for calendar changes
  - Fetches and compares iCal data, computes diffs
  - Triggers email notifications when changes are detected
  - Updates subscription state in the database
- **Deployment:** Runs as a separate Docker container

### 3. **Shared Modules (`shared/`)**

- **Purpose:**
  Contains code shared between API and worker, such as:
  - Database modesl and CRU logic
  - Calendar parsing and validation utilities
  - Token and authentication utilities

### 4. **Frontend (`static/`)**

- **Tech:** HTML, CSS, JavaScript
- **Features:**
  - Responsive, accessible UI for students
  - Internationalization (Croatian/English)
  - Interacts with API endpoints for subscription and management

### 5. **Database**

- **System:** PostgreSQL
- **Purpose:** Stores user subscriptions, calendar metadata, and usage statistics

### 6. **S3 Storage**

- **Default:** MinIO (S3-compatible, runs in Docker)
- **Purpose** Stores calendar files and diffs for efficient processing and auditing

### 7. **Email Service**

- **Options:** SMTP or Resend API (configurable)
- **Purpose:** Sends confirmation, activation, and notification emails to users

### 8. **Redis**

- **Purpose:** Used for rate limiting, cahcing, and email queues (improves performance and security)

---

## Containerization & Deployment

- All major components (API, worker, database, S3, Redis) are run as separate containers via Docker Compose.
- Easy to scale, monitor, and maintain.
- Metrics endpoints are exposed for Prometheus/Grafana.

---

## Security & Privacy

- All sensitive actions require email confirmation or secure API tokens.
- No unnecessary data is collected.
- Open source for full transparency and review.

---

## Extensibility

- The modular design allows FER or other universities to adapt, extend, or integreate NotiFER with existing systems.
- Shared codebase ensures consistency and reduces duplication.

---

For further details, see [UNIVERSITY_DEPLOYMENT.md](UNIVERSITY_DEPLOYMENT.md) and [API_REFERENCE.md](API_REFERENCE.md).
