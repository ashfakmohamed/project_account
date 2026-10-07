# Data Pusher API

A secured Django REST Framework service that receives JSON payloads for an account and forwards them to administrator-configured HTTPS destinations.

## Security model

- Management endpoints require an authenticated Django staff user.
- Management API tokens use Django REST Framework token authentication.
- Each account ingestion token is shown only when issued or rotated; only its hash is stored.
- Destination hosts must be explicitly allowlisted through the environment.
- Forwarding disables redirects and uses a bounded timeout to reduce SSRF and resource-exhaustion risk.
- Databases, virtual environments, and secrets are excluded from Git.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

    python -m pip install -r requirements.txt

3. Configure the variables shown in .env.example. DJANGO_SECRET_KEY is required.
4. Initialize the service:

    python data_pusher/manage.py migrate
    python data_pusher/manage.py createsuperuser
    python data_pusher/manage.py runserver

5. Obtain a management API token:

    python data_pusher/manage.py drf_create_token USERNAME

## API

Authenticated staff management endpoints:

- GET/POST /api/accounts/
- GET/PATCH/DELETE /api/accounts/{id}/
- POST /api/accounts/{id}/rotate-token/
- GET/POST /api/destinations/
- GET/PATCH/DELETE /api/destinations/{id}/

Public ingestion endpoint protected by the account token:

- POST /api/server/incoming-data/
- Header: CL-X-TOKEN: prefix.secret
- Body: any JSON object to forward

The raw account token is returned only at account creation or rotation. Store it securely.

## Tests

    python data_pusher/manage.py check
    python data_pusher/manage.py test
