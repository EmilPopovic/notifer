# 🏗️ NotiFER System Architecture

NotiFER is designed as a modular, scalable, and secure notification platform for university calendar changes.
The system is composed of several cooperating components, each running as a thread in a single Python process for best stability and simplicity.

## Components

### 1. **API Service (`src/api/`)**

- **Framework:** FastAPI (Python)
- **Responsibilities:**
  - Exposes REST endpoints for student and university admin actions
  - Handles subscription management, confirmation, and API authentication
  - Serves the static frontend
  - Provides health and metrics endpoints
- **Deployment:** Runs as a Docker container

### 2. **Calendar Worker (`src/worker/`)**

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

- **System:** SQLite
- **Purpose:** Stores user subscriptions, calendar metadata, and usage statistics

### 6. **Local Storage**

- **Default:** `data/` directory next to `compose.yaml`
- **Purpose** Stores calendar files and diffs for efficient processing and auditing

---

## Security & Privacy

- All sensitive actions require email confirmation or secure API tokens.
- No unnecessary data is collected.
- Open source for full transparency and review.

---

For further details, see [UNIVERSITY_DEPLOYMENT.md](UNIVERSITY_DEPLOYMENT.md) and [API_REFERENCE.md](API_REFERENCE.md).
