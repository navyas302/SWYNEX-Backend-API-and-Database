# Task 1 — Full-Stack Application Architecture

## Product

**JobTrack — Smart Job Application Tracker**

A web application that lets job seekers maintain applications, monitor statuses, record interviews, and view application statistics in one dashboard.

## User Stories

- As a user, I can create an account and log in.
- I can add a job application.
- I can edit or delete an application.
- I can search applications by company, role, or location.
- I can filter by status.
- I can see application statistics on a dashboard.

## Architecture

React Frontend → Flask REST API → SQLAlchemy → SQLite

For production, SQLite can be replaced with MySQL or PostgreSQL.

## Data Models

### User

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| name | String | Required |
| email | String | Unique |
| password | String | Hashed |

### JobApplication

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to User |
| company | String | Required |
| role | String | Required |
| location | String | Optional |
| applied_date | Date/String | Required |
| interview_date | Date/String | Optional |
| status | String | Applied / Interview / Offer / Rejected |
| notes | Text | Optional |

Relationship: one User has many JobApplication records.

## API Routes

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/register | Create account |
| POST | /api/auth/login | Login |
| GET | /api/jobs | List applications |
| POST | /api/jobs | Create application |
| PUT | /api/jobs/:id | Update application |
| DELETE | /api/jobs/:id | Delete application |
| GET | /api/dashboard | Dashboard statistics |
| GET | /api/health | Health check |

## Frontend Screens

1. Login
2. Register
3. Dashboard
4. Application form
5. Application list
6. Search/filter controls

## Security

- Passwords are hashed.
- Protected routes require a JWT.
- Each user can access only their own applications.
- Production deployment should use HTTPS and environment variables for secrets.

## Folder Structure

```text
job_application_tracker/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       └── style.css
├── ARCHITECTURE.md
└── README.md
```

## Future Enhancements

- MySQL/PostgreSQL
- Email interview reminders
- Calendar integration
- Resume upload
- Admin analytics
- Pagination
- Unit/integration tests
- Docker
- Cloud deployment
