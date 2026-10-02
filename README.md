# JobTrack — Smart Job Application Tracker

A full-stack job application tracker built for the SWYNEX Technologies internship tasks.

## Task 2 — Backend & Database

This repository includes the implemented backend and persistence layer for JobTrack.

### Backend stack
- Python
- Flask REST API
- Flask-SQLAlchemy
- SQLite database
- JWT authentication
- Password hashing
- CORS

### Complete resource: Job Applications

The `JobApplication` resource supports:
- **POST** `/api/jobs` — create an application
- **GET** `/api/jobs` — list the logged-in user's applications
- **PUT** `/api/jobs/<id>` — update an application
- **DELETE** `/api/jobs/<id>` — delete an application

### Validation
The API validates:
- Required company, role and applied date
- Date format (`YYYY-MM-DD`)
- Allowed status values: `Applied`, `Interview`, `Offer`, `Rejected`
- Maximum field lengths
- User registration name/email/password
- Invalid status filters

### Persistence
SQLite stores users and job applications through SQLAlchemy. The database is created automatically when the Flask application starts.

### Authentication & security
- Passwords are hashed before storage.
- JWT authentication protects application and dashboard routes.
- Users can access only their own job applications.
- The JWT secret can be supplied through the `SECRET_KEY` environment variable.

## Run Backend

```bash
cd backend
python -m venv venv
# Windows: venv\\Scripts\\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Backend: `http://127.0.0.1:5000`

Health check: `GET /api/health`

## Run Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Demo flow for Task 2

1. Register a user.
2. Log in and receive a JWT token.
3. Add a job application.
4. Show the saved application in the dashboard.
5. Edit and delete an application.
6. Demonstrate validation with an empty field or invalid date/status.
7. Show the dashboard statistics.

## Project structure

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

## Demo video

Add the LinkedIn Task 2 demo/explanation post URL here after publishing it.

`LinkedIn Demo: [paste your Task 2 LinkedIn post URL here]`
