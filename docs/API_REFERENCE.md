# 📖 NotiFER API Reference

This document describes all public API endpoints provided by NotiFER.

---

## Table of contents

- [Student Endpoints](#student-endpoints)
- [University (Admin) Endpoints](#university-admin-endpoints)
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

## University (Admin) Endpoints

> All endpoints below require a Bearer token in the `Authorization` header.

### `POST /uni/subscribe/url`

Add a subscription by calendar URL (activated by default).

**Request:**  

- JSON body:  
  - `q` (string, required): Calendar URL  
  - `language` (string, optional): `hr` or `en`

**Response:**  

- `200 OK` with subscription status

---

### `POST /uni/subscribe/username`

Add a subscription by username and calendar auth (activated by default).

**Request:**  

- JSON body:  
  - `username` (string, required)  
  - `auth` (string, required)  
  - `language` (string, optional): `hr` or `en`

**Response:**  

- `200 OK` with subscription status

---

### `POST /uni/pause`

Pause notifications for a user by username.

**Request:**  

- JSON body: `{ "username": "student123" }`

**Response:**

- `200 OK` with status

---

### `POST /uni/resume`

Resume notifications for a user by username.

**Request:**  

- JSON body: `{ "username": "student123" }`

**Response:**  

- `200 OK` with status

---

### `POST /uni/delete`

Delete a subscription by username.

**Request:**  

- JSON body: `{ "username": "student123" }`

**Response:**  

- `200 OK` with status

---

### `GET /uni/info`

Get subscription info by username.

**Request:**  

- Query params:  
  - `username` (string, required)

**Response:**  

- `200 OK` with subscription details

---

## Health & Monitoring

### `GET /health`

Health check endpoint.

**Response:**

- `200 OK` with status

---

### `GET /metrics`

Prometheus metrics endpoint.

**Response:**

- `200 OK` (Prometheus format)

---

## Error Handling

- All endpoints return standard HTTP status codes.
- Error details are provided in the response body as JSON.

---

## Authentication

- Student endpoints do **not** require authentication (actions are confirmed via email).
- University endpoints require a Bearer token in the `Authorization` header.  
  The SHA-256 hash of the token is stored in the `.env` file.
