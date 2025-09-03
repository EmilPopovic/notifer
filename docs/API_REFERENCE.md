# 📖 NotiFER API Reference

This document describes all public API endpoints provided by NotiFER.

---

## Table of contents

- [Student Endpoints](#student-endpoints)
- [Admin Endpoints](#admin-endpoints)
- [Health & Monitoring](#health--monitoring)
- [Error Handling](#error-handling)
- [Authentication](#authentication)

---

## Student Endpoints

### `POST /subscribe`

Subscribe to notifications using a FER calendar URL (sends confirmatio email).

**Request:**

- Query params:
  - `q` (string, required): Calendar URL
  - `language` (string, optional): `hr` or `en`

**Response:**

- `200 OK` with subscription status

---

### `GET /activate`

Activate a subscription via email confirmation link.

**Request:**

- Query params:
  - `token` (string, required): Activation token

**Response:**

- `200 OK` with activation status (HTML)

---

### `POST /request-delete`

Request deletion of a subscription (sends confirmation email).

**Request:**

- JSON body: `{ "email": "user@fer.hr" }`

**Response:**

- `200 OK` with status

---

### `GET /delete`

Delete a subscription via email confirmation link.

**Request:**

- Query params:
  - `token` (string, required): Deletion token

**Response:**

- `200 OK` with deletion status (HTML)

---

### `POST /request-pause`

Request to pause notifications (sends confirmation email).

**Request:**  

- JSON body: `{ "email": "user@fer.hr" }`

**Response:**  

- `200 OK` with status

---

### `GET /pause`

Pause notifications via email confirmation link.

**Request:**  

- Query params:  
  - `token` (string, required): Pause token

**Response:**  

- `200 OK` with status (HTML)

---

### `POST /request-resume`

Request to resume notifications (sends confirmation email).

**Request:**  

- JSON body: `{ "email": "user@fer.hr" }`

**Response:**  

- `200 OK` with status

---

### `GET /resume`

Resume notifications via email confirmation link.

**Request:**  

- Query params:  
  - `token` (string, required): Resume token

**Response:**  

- `200 OK` with status (HTML)

---

## Admin Endpoints

> All endpoints below require a Bearer token in the `Authorization` header.

### `POST /admin/subscribe/url`

Add a subscription by calendar URL (activated by default).

**Request:**  

- JSON body:  
  - `q` (string, required): Calendar URL  
  - `language` (string, optional): `hr` or `en`

**Response:**  

- `200 OK` with subscription status

**Usage:**

```bash
curl -X POST <base-url>/admin/subscribe/url \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"q": "<calendar-url>", "language": "<lang>"}'
```

---

### `POST /admin/subscribe/username`

Add a subscription by username and calendar auth (activated by default).

**Request:**  

- JSON body:  
  - `username` (string, required)  
  - `auth` (string, required)  
  - `language` (string, optional): `hr` or `en`

**Response:**  

- `200 OK` with subscription status

**Usage:**

```bash
curl -X POST <base-url>/admin/subscribe/username \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"username": "<username>", "auth": "<calendar-auth>", "language": "<lang>"}'
```

---

### `POST /admin/pause`

Pause notifications for a user by username.

**Request:**  

- JSON body: `{ "username": "student123" }`

**Response:**

- `200 OK` with status

**Usage:**

```bash
curl -X POST <base-url>/admin/pause \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"username": "<username>"}'
```

---

### `POST /admin/resume`

Resume notifications for a user by username.

**Request:**  

- JSON body: `{ "username": "student123" }`

**Response:**  

- `200 OK` with status

**Usage:**

```bash
curl -X POST <base-url>/admin/resume \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"username": "<username>"}'
```

---

### `POST /admin/delete`

Delete a subscription by username.

**Request:**  

- JSON body: `{ "username": "student123" }`

**Response:**  

- `200 OK` with status

**Usage:**

```bash
curl -X POST <base-url>/admin/delete \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"username": "<username>"}'
```

---

### `GET /admin/info`

Get subscription info by username.

**Request:**  

- Query params:  
  - `username` (string, required)

**Response:**  

- `200 OK` with subscription details

**Usage:**

```bash
curl -X GET "<base-url>/admin/info?username=<username>" \
  -H "Authorization: Bearer <token>"
```

### `GET /admin/info/all`

Get info about all subscriptions.

**Response:**  

- `200 OK` with list of subscription details

**Usage:**

```bash
curl -X GET "<base-url>/admin/info/all" \
  -H "Authorization: Bearer <token>"
```

---

## Health & Monitoring

### `GET /health`

Health check endpoint.

**Response:**

- `200 OK` with status

### `GET /health/ready`

Kubernetes-style readiness check.

**Respnse:**

- `200 OK` with `{'status': 'ready'}`

### `GET /health/detailed`

Detailed healthcheck with dependency verification. This endpoint is protected.

**Response:**

- `200 OK` with status of API, worker and database.

**Usage:**

```bash
curl -X GET "<base-url>/health/detailed" \
  -H "Authorization: Bearer <token>"
```

### `GET /stats`

Stats of the app. This is a protected endpoint.

**Response:**

```bash
{
  'timestamp': <current timestamp>,
  'total_subscriptions': <total number of subscriptions>,
  'active_subscriptions': <total number of active and unpaused subscriptions>,
  'total_changes_detected': <number of times a calendar change has been detected in all sessions>,
  'email_queue_size': <number of emails currently queued for sending>,
  'worker_cycles_total': <number of checking cycles since start of current session>,
  'worker_cycle_duration': <time taken for the last cycle>,
  'worker_last_cycle': <timestamp of the last cycle>,
  'subscriptions_processed': worker_service.subscriptions_processed,
  'calendar_fetches': <total number of times calendars have been fetched in the current session>,
  'calendar_fetch_duration': <time spent fetching calendars in the last cycle>,
  'emails_queued': <total number of enqueued emails since the start of current session>,
}
```

**Usage:**

```bash
curl -X GET "<base-url>/stats" \
  -H "Authorization: Bearer <token>"
```

---

## Error Handling

- All endpoints return standard HTTP status codes.
- Error details are provided in the response body as JSON.

---

## Authentication

- Student endpoints do **not** require authentication (actions are confirmed via email).
- Admin endpoints require a Bearer token in the `Authorization` header.  
  The SHA-256 hash of the token is stored in the `.env` file.
