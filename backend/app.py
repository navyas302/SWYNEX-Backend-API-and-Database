from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date, datetime, timezone, timedelta
import jwt
import os
import re

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jobtracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
db = SQLAlchemy(app)

ALLOWED_STATUSES = {"Applied", "Interview", "Offer", "Rejected"}
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    company = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), default="")
    applied_date = db.Column(db.String(10), nullable=False)
    interview_date = db.Column(db.String(10), default="")
    status = db.Column(db.String(30), default="Applied", nullable=False)
    notes = db.Column(db.Text, default="")


def token_for(user):
    return jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        },
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"message": "Authorization token required"}), 401
        try:
            payload = jwt.decode(
                header.split(" ", 1)[1],
                app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )
            user = db.session.get(User, payload["user_id"])
            if not user:
                raise ValueError()
        except Exception:
            return jsonify({"message": "Invalid or expired token"}), 401
        return fn(user, *args, **kwargs)

    return wrapper


def clean(value, field, max_length):
    if value is None:
        return ""
    value = str(value).strip()
    if len(value) > max_length:
        raise ValueError(f"{field} must be {max_length} characters or fewer")
    return value


def valid_date(value, field, required=False):
    value = clean(value, field, 10)
    if not value:
        if required:
            raise ValueError(f"{field} is required")
        return ""
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{field} must use YYYY-MM-DD format")
    return value


def validate_job(data, partial=False):
    data = data or {}
    result = {}

    if not partial or "company" in data:
        result["company"] = clean(data.get("company"), "Company", 120)
        if not result["company"]:
            raise ValueError("Company is required")

    if not partial or "role" in data:
        result["role"] = clean(data.get("role"), "Role", 120)
        if not result["role"]:
            raise ValueError("Role is required")

    if not partial or "applied_date" in data:
        result["applied_date"] = valid_date(data.get("applied_date"), "Applied date", required=True)

    if "location" in data:
        result["location"] = clean(data.get("location"), "Location", 120)
    if "interview_date" in data:
        result["interview_date"] = valid_date(data.get("interview_date"), "Interview date")
    if "status" in data:
        status = clean(data.get("status"), "Status", 30)
        if status not in ALLOWED_STATUSES:
            raise ValueError("Status must be Applied, Interview, Offer, or Rejected")
        result["status"] = status
    if "notes" in data:
        result["notes"] = clean(data.get("notes"), "Notes", 2000)

    return result


def job_json(j):
    return {
        "id": j.id,
        "company": j.company,
        "role": j.role,
        "location": j.location,
        "applied_date": j.applied_date,
        "interview_date": j.interview_date,
        "status": j.status,
        "notes": j.notes,
    }


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/auth/register")
def register():
    data = request.get_json() or {}
    try:
        name = clean(data.get("name"), "Name", 100)
        email = clean(data.get("email"), "Email", 120).lower()
        password = data.get("password", "")
        if not name:
            raise ValueError("Name is required")
        if not EMAIL_RE.match(email):
            raise ValueError("A valid email is required")
        if not isinstance(password, str) or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        if len(password) > 128:
            raise ValueError("Password must be 128 characters or fewer")
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409

    user = User(name=name, email=email, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({"token": token_for(user), "user": {"id": user.id, "name": user.name, "email": user.email}}), 201


@app.post("/api/auth/login")
def login():
    data = request.get_json() or {}
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401
    return jsonify({"token": token_for(user), "user": {"id": user.id, "name": user.name, "email": user.email}})


@app.get("/api/jobs")
@auth_required
def jobs(user):
    status = request.args.get("status", "")
    q = request.args.get("q", "").strip().lower()
    query = JobApplication.query.filter_by(user_id=user.id)
    if status:
        if status not in ALLOWED_STATUSES:
            return jsonify({"message": "Invalid status filter"}), 400
        query = query.filter_by(status=status)
    applications = query.order_by(JobApplication.id.desc()).all()
    if q:
        applications = [
            j for j in applications
            if q in j.company.lower() or q in j.role.lower() or q in (j.location or "").lower()
        ]
    return jsonify([job_json(j) for j in applications])


@app.post("/api/jobs")
@auth_required
def create_job(user):
    try:
        values = validate_job(request.get_json(), partial=False)
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400

    j = JobApplication(user_id=user.id, **values)
    db.session.add(j)
    db.session.commit()
    return jsonify(job_json(j)), 201


@app.put("/api/jobs/<int:job_id>")
@auth_required
def update_job(user, job_id):
    j = JobApplication.query.filter_by(id=job_id, user_id=user.id).first()
    if not j:
        return jsonify({"message": "Application not found"}), 404
    try:
        values = validate_job(request.get_json(), partial=True)
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400
    for key, value in values.items():
        setattr(j, key, value)
    db.session.commit()
    return jsonify(job_json(j))


@app.delete("/api/jobs/<int:job_id>")
@auth_required
def delete_job(user, job_id):
    j = JobApplication.query.filter_by(id=job_id, user_id=user.id).first()
    if not j:
        return jsonify({"message": "Application not found"}), 404
    db.session.delete(j)
    db.session.commit()
    return jsonify({"message": "Application deleted"})


@app.get("/api/dashboard")
@auth_required
def dashboard(user):
    applications = JobApplication.query.filter_by(user_id=user.id).all()
    counts = {status: sum(1 for j in applications if j.status == status) for status in ALLOWED_STATUSES}
    return jsonify({"total": len(applications), "counts": counts})


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
