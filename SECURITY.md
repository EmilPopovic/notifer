# Security Policy

## Overview

NotiFER is designed with privacy and security as top priorities.
This document outlines the security practices, responsible disclosure process, and recommendations for safe deployment and operation.

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| latest  | Yes                |
| older   | No (please update) |

## Reporting a Vulnerability

If you discover a security vulnerability, **please report it privately** to the maintainer:

- **Email:** [admin@emilpopovic.me](mailto:admin@emilpopovic.me)

Do **not** create public GitHub issues for security problems.
We will respond as quickly as possible and coordinate a fix and disclosure.

## Security Features

- **API Authentication:**
  All administrative endpoints require a secure Bearer token. The token hash is stored in environment variables and never in code or logs.

- **Email Confirmation:**
  All sensitive student actions (activation, deletion, pause/resume) require confirmation via a unique, expiring email token.

- **Data Minimization:**
  Only essential data is stored (email, calendar auth, language). No unnecessary personal information is collected.

- **GDPR-Friendly:**
  Users can delete their data at any time. No tracking or analytics are performed.

- **Rate Limiting:**
  Rate limiting is available to prevent abuse on email-sending endpoints.

- **Open Source:**
  The codebase is fully open for audit by any interested party.

## Deployment Recommendations

- **Use HTTPS:**
  Always deploy behind a secure reverse proxy with HTTPS enabled.

- **Protect API Tokens:**
  Store API tokens and secrets in environment variables or secure secrets managers.
  Never commit secrets to version control.

- **Update Regularly:**
  Keep NotiFER and all dependencies up to date to receive security patches.

- **Restrict Access:**
  Limit access to the admin API endpoints to trusted systems/networks.

- **Monitor Logs and Metrics:**
  Regularly review logs and metrics for unusual activity.

## Responsible Disclosure

We encourage responsible disclosure of security issues.
If you have questions or concerns about NotiFER's security, please contact the maintainer directly.

Thank you for helping keep NotiFER and its users safe!
