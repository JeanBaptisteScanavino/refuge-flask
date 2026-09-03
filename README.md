# 🎮 Refuge - Streamer Management Platform

A modern Flask-based platform for managing Twitch streamers with integrated OAuth token refresh and admin-provisioned user accounts.

## Overview

Refuge is a secure, production-ready application that allows authenticated users to:
- Browse and manage a shared list of Twitch streamers
- Retrieve detailed information about streamers (followers, statistics, etc.)
- Refresh Twitch OAuth tokens automatically
- Export streamer lists in Markdown format

The application uses **Flask-SQLAlchemy** for data persistence, **PostgreSQL 16** for the database, and **Docker** for containerized deployment.

## Features

✅ **Authentication & Authorization**
- Session-based login with werkzeug password hashing
- No public registration (admin-provisioned users only)
- Flask-Login integration for secure user management

✅ **Streamer Management**
- Create and list Twitch streamers
- Verify streamers via Twitch Helix API
- Shared global streamer database
- One-click streamer information lookup

✅ **Twitch Integration**
- Real Twitch API integration (Helix + OAuth2)
- Client credentials flow for token refresh
- Follower count retrieval
- TwitchTracker integration for stats

✅ **Admin Tooling**
- CLI command for user provisioning: `flask create-user`
- Secure credential storage (client_id, client_secret)
- Database migration management (Alembic)

✅ **User Interface**
- Modern, responsive design
- Left sidebar navigation with token status
- Create streamer form at top
- Streamer list with hover effects
- Error messages with visual feedback

## Architecture

```
app/
├── __init__.py           # App factory, extensions, blueprint registration
├── config.py             # Configuration (SECRET_KEY, DATABASE_URL, etc.)
├── cli.py                # CLI commands (create-user)
├── db/
│   ├── models.py         # SQLAlchemy ORM models (User, Streamer)
│   └── repository.py     # Data access layer (abstract + concrete)
├── core/
│   ├── exceptions.py     # Custom exception hierarchy
│   ├── auth_usecase.py   # Authentication & token refresh logic
│   ├── streamers_usecase.py  # Streamer creation
│   └── infos_usecase.py  # Streamer info lookup
├── utils/
│   └── twitch_client.py  # Twitch API clients (Helix, OAuth, TwitchTracker)
├── auth/
│   └── routes.py         # JSON endpoints (/auth/login, /auth/logout)
├── main/
│   └── routes.py         # HTML form routes (/, /login, /logout, /streamers, /token)
├── users/
│   └── routes.py         # JSON user endpoints (/users/me/token/refresh)
├── streamers/
│   └── routes.py         # JSON streamer endpoints (POST/GET /streamers/, /streamers/<username>, /streamers/all)
├── extensions.py         # Flask extension instances (db, login_manager)
└── templates/
    └── home.html         # Main UI template
```

**Design Pattern**: Layered architecture with separated concerns:
- **Routes**: HTTP request handling
- **Usecases**: Business logic
- **Repository**: Data access abstraction
- **Models**: ORM definitions

## Requirements

- **Python** 3.12+
- **Docker** & Docker Compose
- **PostgreSQL** 16 (via Docker)
- **Twitch Developer Account** (for client_id and client_secret)

## Quick Start

### 1. Clone & Setup

```bash
cd /home/barbadoug/refuge-flask
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with production values:

```env
# Security (MUST change before production)
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Flask
FLASK_APP=wsgi.py
FLASK_ENV=production
FLASK_DEBUG=False

# Database
POSTGRES_USER=refuge
POSTGRES_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(24))")
POSTGRES_DB=refuge
DATABASE_URL=postgresql://refuge:password@db:5432/refuge
```

### 3. Build & Run

**Development Mode** (auto-reloader enabled):
```bash
docker compose up -d
```

**Production Mode** (gunicorn + optimized):
```bash
# Update docker-compose.yml target to "production"
docker compose -f docker-compose.yml up -d
```

### 4. Initialize Database

```bash
docker compose exec web flask db upgrade
```

### 5. Create First User

```bash
docker compose exec web flask create-user <username> <client-id> <client-secret>
```

When prompted, enter a secure password for the user.

## API Endpoints

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/login` | — | Form-based login |
| POST | `/logout` | ✓ | Logout user |
| POST | `/auth/login` | — | JSON login endpoint |
| POST | `/auth/logout` | ✓ | JSON logout endpoint |

### Token Management

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/token` | ✓ | Form: Refresh Twitch token |
| POST | `/users/me/token/refresh` | ✓ | JSON: Refresh Twitch token |

### Streamers

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/streamers` | ✓ | Form: Create streamer |
| POST | `/streamers/` | ✓ | JSON: Create streamer |
| GET | `/streamers/<username>` | ✓ | Get streamer info (JSON/HTML) |
| GET | `/streamers/all` | ✓ | List all streamers (Markdown) |

### Example Requests

**Login (JSON)**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}'
```

**Create Streamer (JSON)**
```bash
curl -X POST http://localhost:5000/streamers/ \
  -H "Content-Type: application/json" \
  -d '{"username":"eliacheff"}' \
  -b "session=<cookie>"
```

**Get Streamer Info**
```bash
curl http://localhost:5000/streamers/eliacheff \
  -b "session=<cookie>"
```

**Export Streamers (Markdown)**
```bash
curl http://localhost:5000/streamers/all \
  -b "session=<cookie>"
```

## Database Schema

### Users Table
```sql
id (PK)
username (UNIQUE, VARCHAR)
password_hash (VARCHAR)
twitch_client_id (VARCHAR)
twitch_client_secret (VARCHAR)
twitch_token (VARCHAR)
created_at (TIMESTAMP)
```

### Streamers Table
```sql
id (PK)
username (VARCHAR)
username_lower (UNIQUE, VARCHAR)
broadcaster_id (VARCHAR)
```

### Database Migrations

```bash
# Create migration
docker compose exec web flask db migrate -m "description"

# Apply migrations
docker compose exec web flask db upgrade

# Downgrade
docker compose exec web flask db downgrade
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `"dev"` | Flask secret key (MUST change in production) |
| `FLASK_ENV` | `development` | `development` or `production` |
| `FLASK_DEBUG` | `True` | Enable debug mode (disable in production) |
| `DATABASE_URL` | — | PostgreSQL connection string |
| `POSTGRES_USER` | `refuge` | Database username |
| `POSTGRES_PASSWORD` | `refuge` | Database password |
| `POSTGRES_DB` | `refuge` | Database name |

**Last Updated**: September 3, 2026
**Version**: 1.0.0-production
