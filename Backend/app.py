from __future__ import annotations

import json
import hashlib
import os
import random
import re
import sqlite3
import secrets
from io import BytesIO
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env", override=True)
DEFAULT_DB_PATH = Path("/tmp/peopleos-workforce.db") if os.getenv("VERCEL") else ROOT / "Backend" / "workforce_management.db"
DB_PATH = Path(os.getenv("PEOPLEOS_DB_PATH", str(DEFAULT_DB_PATH)))
FRONTEND_PATH = ROOT / "Frontend"

app = FastAPI(title="PeopleOS Workforce Intelligence", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=3, max_length=120)


class PolicyQuestion(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class RoleCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    department: str = Field(min_length=2, max_length=80)
    status: str = Field(default="New", max_length=40)


class ApplicantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    role: str = Field(min_length=2, max_length=120)
    experience: str = Field(min_length=1, max_length=80)
    skills: str = Field(min_length=2, max_length=300)
    stage: str = Field(default="New", max_length=40)


class PolicyCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    section: str = Field(min_length=2, max_length=80)
    content: str = Field(min_length=10, max_length=3000)


class RegistrationRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=8, max_length=120)
    confirm_password: str = Field(min_length=8, max_length=120)
    role: str = Field(min_length=2, max_length=60)


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=8, max_length=120)
    confirm_password: str = Field(min_length=8, max_length=120)
    role: str = Field(min_length=2, max_length=60)


class ProfileUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=3, max_length=120)
    password: str | None = Field(default=None, min_length=8, max_length=120)
    confirm_password: str | None = Field(default=None, min_length=8, max_length=120)


class LearningPlanCreate(BaseModel):
    employee_id: int
    skill: str = Field(min_length=2, max_length=120)
    title: str = Field(min_length=2, max_length=160)


class EmployeeUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    role: str = Field(min_length=2, max_length=120)
    department: str = Field(min_length=2, max_length=80)
    location: str = Field(min_length=2, max_length=120)
    skills: str = Field(min_length=2, max_length=400)
    performance_score: float = Field(ge=0, le=5)
    satisfaction_score: float = Field(ge=0, le=5)
    overtime: int = Field(ge=0, le=1)


class FireEmployeeRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)


class KPIWeightUpdate(BaseModel):
    role_kpi_id: str = Field(min_length=2, max_length=60)
    weight: float = Field(ge=0, le=1)


class RoleKPIConfigUpdate(BaseModel):
    items: list[KPIWeightUpdate] = Field(min_length=1, max_length=30)


class InterviewCreate(BaseModel):
    candidate_id: str = Field(min_length=2, max_length=50)
    job_id: str = Field(min_length=2, max_length=50)
    interview_round: int = Field(ge=1, le=20)
    interview_date: str | None = None


class InterviewAnswerCreate(BaseModel):
    question_id: str = Field(min_length=2, max_length=50)
    answer_text: str = Field(min_length=1, max_length=10000)


class CandidateStatusUpdate(BaseModel):
    status: str = Field(min_length=2, max_length=40)


class JobRequirementCreate(BaseModel):
    skill_id: str = Field(min_length=2, max_length=80)
    required_proficiency: str = Field(min_length=2, max_length=40)
    required_proficiency_score: float = Field(ge=0, le=100)
    weight: float = Field(ge=0, le=1)
    is_mandatory: bool = False
    requirement_type: str = Field(default="skill", max_length=40)
    minimum_years: float | None = Field(default=None, ge=0, le=80)
    description: str | None = Field(default=None, max_length=500)


class CandidateCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    location: str | None = Field(default=None, max_length=100)
    total_experience_years: float | None = Field(default=None, ge=0, le=80)
    highest_education: str | None = Field(default=None, max_length=100)
    education_field: str | None = Field(default=None, max_length=100)
    current_role: str | None = Field(default=None, max_length=100)


POLICY_STOPWORDS = {"about", "after", "also", "can", "days", "from", "how", "many", "what", "when", "where", "which", "with"}
ROLE_OPTIONS = {"Recruiter", "Hiring Manager", "HR Manager", "HR Business Partner", "HR Admin"}
JOB_STATUS_OPTIONS = {"New", "Screening", "Interviewing", "Offer", "Closed"}


def password_hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class GeminiService:
    """Single server-side boundary for all generative AI work."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY")
        configured_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        retired_models = {"gemini-2.5-flash-lite", "gemini-2.0-flash"}
        self.model_name = "gemini-3.5-flash-lite" if configured_model in retired_models else configured_model

    async def answer_policy_question(self, question: str, context: list[dict[str, str]]) -> dict[str, Any]:
        question_terms = {term for term in re.findall(r"[a-z0-9]+", question.lower()) if len(term) > 3 and term not in POLICY_STOPWORDS}
        relevant = [item for item in context if question_terms.intersection(set(re.findall(r"[a-z0-9]+", item["content"].lower())))]
        if not relevant:
            relevant = context

        if not self.api_key:
            return self.local_policy_answer(question, relevant, configured=False)

        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)
            source_text = "\n\n".join(
                f"{item['title']} ({item['section']}):\n{item['content']}" for item in relevant
            )
            prompt = (
                "You are an HR policy assistant. Answer only from the supplied policy excerpts. "
                "If the excerpts do not contain the answer, say so and set needs_hr_review to true. "
                "Return valid JSON with answer, sources, and needs_hr_review.\n\n"
                f"Question: {question}\n\nPolicy excerpts:\n{source_text}"
            )
            response = client.models.generate_content(model=self.model_name, contents=prompt)
            text = response.text or ""
            start, end = text.find("{"), text.rfind("}")
            parsed = json.loads(text[start:end + 1])
            return {**parsed, "sources": parsed.get("sources", [item["title"] for item in relevant]), "configured": True}
        except Exception:
            return self.local_policy_answer(question, relevant, configured=True)

    @staticmethod
    def local_policy_answer(question: str, context: list[dict[str, str]], configured: bool) -> dict[str, Any]:
        question_terms = {term for term in re.findall(r"[a-z0-9]+", question.lower()) if len(term) > 3 and term not in POLICY_STOPWORDS}
        matching = [item for item in context if question_terms.intersection(set(re.findall(r"[a-z0-9]+", item["content"].lower())))]
        if matching:
            answer = matching[0]["content"]
            review = False
        else:
            answer = "No policy source directly answers that question. HR should verify the request before giving guidance."
            review = True
        return {"answer": answer, "sources": [item["title"] for item in (matching or context)], "needs_hr_review": review, "configured": configured, "fallback": True}

    async def answer_hr_chat(self, message: str, context: str) -> dict[str, Any]:
        if not self.api_key:
            return {"answer": "The HR assistant is not configured yet. Please ask HR or use the relevant workspace page.", "configured": False}
        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)
            prompt = (
                "You are PeopleOS HR Copilot. Help HR users navigate this workforce platform. "
                "Use the supplied context when answering data questions. Never invent policies, employee facts, "
                "or actions. Explain that hiring, firing, and account changes require a human decision. "
                "Keep the answer concise and practical.\n\n"
                f"Workspace context:\n{context}\n\nUser message:\n{message}"
            )
            response = client.models.generate_content(model=self.model_name, contents=prompt)
            return {"answer": response.text or "I could not generate a response.", "configured": True}
        except Exception:
            return {"answer": "The HR assistant is temporarily unavailable. Please use the workspace data directly or try again.", "configured": True}

    def analyze_feedback(self, comments: list[str]) -> dict[str, Any]:
        text = " ".join(comment for comment in comments if comment).strip()
        if not text:
            return {"strengths": [], "weaknesses": [], "skills_mentioned": [], "positive_evidence": [], "negative_evidence": [], "development_areas": []}
        if self.api_key:
            try:
                from google import genai

                client = genai.Client(api_key=self.api_key)
                prompt = (
                    "Analyze the supplied HR feedback without changing any numerical performance score. "
                    "Return valid JSON with strengths, weaknesses, skills_mentioned, positive_evidence, "
                    "negative_evidence, and development_areas as arrays of concise strings.\n\n"
                    f"Feedback:\n{text}"
                )
                response = client.models.generate_content(model=self.model_name, contents=prompt)
                raw = response.text or "{}"
                start, end = raw.find("{"), raw.rfind("}")
                result = json.loads(raw[start:end + 1])
                return {key: result.get(key, []) for key in ("strengths", "weaknesses", "skills_mentioned", "positive_evidence", "negative_evidence", "development_areas")}
            except Exception:
                pass
        positive_terms = ("strong", "good", "excellent", "delivers", "analytical", "proactive")
        negative_terms = ("improve", "needs", "inconsistent", "development", "miss", "weak")
        positive = [comment for comment in comments if any(term in comment.lower() for term in positive_terms)]
        negative = [comment for comment in comments if any(term in comment.lower() for term in negative_terms)]
        return {
            "strengths": ["Positive feedback evidence present"] if positive else [],
            "weaknesses": ["Development feedback evidence present"] if negative else [],
            "skills_mentioned": [],
            "positive_evidence": positive[:4],
            "negative_evidence": negative[:4],
            "development_areas": ["Review recurring development feedback"] if negative else [],
        }

    @staticmethod
    def parse_resume_contact_fields(text: str) -> dict[str, str | None]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        email_match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, flags=re.IGNORECASE)
        phone_match = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text)
        location_match = re.search(r"(?:\b(?:City|State|Country|Location)\b[:\-]?\s*)?([A-Z][A-Za-z.-]+(?:,\s*[A-Z][A-Za-z.-]+){0,2}|[A-Z][A-Za-z.-]+\s+[A-Z][A-Za-z.-]+)", text)
        name = None
        for line in lines:
            lowered = line.lower()
            if "@" in line or any(token in lowered for token in ("resume", "cv", "curriculum", "summary", "skills", "experience", "education", "certifications", "projects")):
                continue
            if len(line.split()) <= 5 and not re.fullmatch(r"[0-9\s()+.-]+", line):
                name = line
                break
        if location_match:
            location = location_match.group(1).strip()
            if location.lower() in {"resume", "cv", "profile", "summary"}:
                location = None
        else:
            location = None
        return {
            "name": name,
            "email": email_match.group(0).strip() if email_match else None,
            "phone": phone_match.group(0).strip() if phone_match else None,
            "location": location,
        }

    def extract_resume_profile(self, text: str, pdf_content: bytes | None = None, filename: str = "resume.pdf") -> dict[str, Any]:
        contact = self.parse_resume_contact_fields(text)
        empty = {
            "name": contact.get("name"),
            "email": contact.get("email"),
            "phone": contact.get("phone"),
            "location": contact.get("location"),
            "skills": [],
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
            "evidence_status": "not_found",
        }
        if not text.strip() and not pdf_content:
            return empty
        if self.api_key:
            uploaded_file = None
            try:
                from google import genai

                client = genai.Client(api_key=self.api_key)
                prompt = (
                    "Extract only information explicitly present in this resume. Never infer or invent. "
                    "Return JSON only with exactly these keys: name, email, phone, location, skills, experience, projects, education, certifications. "
                    "Skills must contain name, proficiency, confidence, evidence. "
                    "Experience must contain title, company, duration, description, technologies. "
                    "Projects must contain name, description, technologies. "
                    "Education must contain degree, field, institution, year. "
                    "Certifications must contain name, organization. Use null or not_found when absent."
                )
                contents: Any = prompt + f"\n\nResume text fallback:\n{text}"
                if pdf_content:
                    uploaded_file = client.files.upload(file=BytesIO(pdf_content), config={"display_name": filename, "mime_type": "application/pdf"})
                    contents = [uploaded_file, prompt]
                response = client.models.generate_content(model=self.model_name, contents=contents)
                raw = response.text or "{}"
                start, end = raw.find("{"), raw.rfind("}")
                result = json.loads(raw[start:end + 1])
                merged = {**empty, **result}
                for key, value in contact.items():
                    if value and not merged.get(key):
                        merged[key] = value
                return {**merged, "evidence_status": "extracted"}
            except Exception:
                pass
        return {**empty, "evidence_status": "stored_only", "source_text": text}


ai_service = GeminiService()


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def ensure_dataset_compatibility(db: sqlite3.Connection) -> None:
    incompatible_tables = {
        "learning_plans": """
            CREATE TABLE learning_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                skill TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Planned',
                created_at TEXT NOT NULL
            )
        """,
        "attrition_predictions": """
            CREATE TABLE attrition_predictions (
                employee_id INTEGER PRIMARY KEY,
                risk_score REAL NOT NULL,
                factors TEXT NOT NULL
            )
        """,
    }
    for table_name, create_sql in incompatible_tables.items():
        foreign_keys = db.execute(f"PRAGMA foreign_key_list({table_name})").fetchall()
        if any(row["table"] == "employees" and row["to"] == "id" for row in foreign_keys):
            columns = [row["name"] for row in db.execute(f"PRAGMA table_info({table_name})").fetchall()]
            rows = db.execute(f"SELECT {', '.join(columns)} FROM {table_name}").fetchall()
            db.execute(f"DROP TABLE {table_name}")
            db.execute(create_sql)
            if rows:
                placeholders = ", ".join("?" for _ in columns)
                db.executemany(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})", [tuple(row) for row in rows])

    employee_columns = {row["name"] for row in db.execute("PRAGMA table_info(employees)").fetchall()}
    employee_compatibility = {
        "id": "INTEGER",
        "name": "TEXT",
        "role": "TEXT",
        "department": "TEXT",
        "tenure_years": "REAL",
        "performance_score": "REAL",
        "satisfaction_score": "REAL",
        "overtime": "INTEGER",
        "skills": "TEXT",
        "status": "TEXT",
        "fired_by": "TEXT",
        "firing_reason": "TEXT",
    }
    for column, definition in employee_compatibility.items():
        if column not in employee_columns:
            db.execute(f"ALTER TABLE employees ADD COLUMN {column} {definition}")

    job_columns = {row["name"] for row in db.execute("PRAGMA table_info(jobs)").fetchall()}
    job_compatibility = {
        "id": "INTEGER",
        "title": "TEXT",
        "department": "TEXT",
        "applicants": "INTEGER DEFAULT 0",
    }
    for column, definition in job_compatibility.items():
        if column not in job_columns:
            db.execute(f"ALTER TABLE jobs ADD COLUMN {column} {definition}")

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            experience TEXT NOT NULL,
            skills TEXT NOT NULL,
            stage TEXT NOT NULL,
            match_score INTEGER NOT NULL DEFAULT 70
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS job_skills (
            job_skill_id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            skill_id TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'job_requirement',
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS candidate_resume_extractions (
            extraction_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            source_document TEXT NOT NULL,
            extraction_json TEXT NOT NULL,
            extraction_status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id)
        )
        """
    )
    db.execute("INSERT OR IGNORE INTO job_skills (job_skill_id, job_id, skill_id) SELECT 'JS_' || job_requirement_id, job_id, skill_id FROM job_requirements")

    if "employee_id" in employee_columns:
        db.execute(
            """
            UPDATE employees
            SET id = CAST(SUBSTR(employee_id, 4) AS INTEGER),
                name = TRIM(first_name || ' ' || last_name),
                role = COALESCE((SELECT role_name FROM roles WHERE roles.role_id = employees.role_id), role),
                department = COALESCE((SELECT department_name FROM departments WHERE departments.department_id = employees.department_id), department),
                tenure_years = ROUND((JULIANDAY('2026-06-30') - JULIANDAY(date_of_joining)) / 365.25, 1),
                performance_score = COALESCE((SELECT overall_score / 20.0 FROM employee_performance_history p WHERE p.employee_id = employees.employee_id ORDER BY p.period_end DESC LIMIT 1), 3.5),
                satisfaction_score = COALESCE((SELECT AVG(overall_rating) FROM employee_feedback f WHERE f.employee_id = employees.employee_id), 3.5),
                overtime = CASE WHEN COALESCE((SELECT SUM(overtime_hours) FROM employee_attendance a WHERE a.employee_id = employees.employee_id), 0) >= 8 THEN 1 ELSE 0 END,
                skills = COALESCE((SELECT GROUP_CONCAT(skill_id, ', ') FROM employee_skills s WHERE s.employee_id = employees.employee_id), ''),
                status = CASE LOWER(employment_status) WHEN 'active' THEN 'Active' WHEN 'terminated' THEN 'Fired' WHEN 'leave' THEN 'Leave' ELSE 'Active' END
            WHERE name IS NULL OR name = ''
            """
        )
        db.execute(
            """
            UPDATE jobs
            SET id = CAST(SUBSTR(job_id, 4) AS INTEGER),
                title = job_title,
                department = COALESCE((SELECT department_name FROM departments WHERE departments.department_id = jobs.department_id), department),
                applicants = COALESCE((SELECT COUNT(*) FROM candidate_job_scores s WHERE s.job_id = jobs.job_id), 0),
                status = CASE LOWER(jobs.status) WHEN 'open' THEN 'New' WHEN 'filled' THEN 'Closed' WHEN 'closed' THEN 'Closed' ELSE 'Screening' END
            WHERE title IS NULL OR title = ''
            """
        )
        if db.execute("SELECT COUNT(*) FROM applicants").fetchone()[0] == 0:
            db.execute(
                """
                INSERT INTO applicants (id, name, role, experience, skills, stage, match_score)
                SELECT CAST(SUBSTR(c.candidate_id, 4) AS INTEGER),
                       TRIM(c.first_name || ' ' || c.last_name),
                       COALESCE(c.current_role, 'Candidate'),
                       printf('%.1f years', c.total_experience_years),
                       COALESCE((SELECT GROUP_CONCAT(skill_id, ', ') FROM candidate_skills s WHERE s.candidate_id = c.candidate_id), ''),
                       CASE LOWER(c.status) WHEN 'screening' THEN 'Screening' WHEN 'interview' THEN 'Interviewing' WHEN 'hired' THEN 'Hired' WHEN 'rejected' THEN 'Rejected' ELSE 'New' END,
                       COALESCE(ROUND((SELECT AVG(overall_match_score) FROM candidate_job_scores score WHERE score.candidate_id = c.candidate_id)), 70)
                FROM candidates c
                """
            )


def seed_database() -> None:
    with closing(connect()) as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                department TEXT NOT NULL,
                location TEXT NOT NULL,
                tenure_years REAL NOT NULL,
                performance_score REAL NOT NULL,
                satisfaction_score REAL NOT NULL,
                overtime INTEGER NOT NULL,
                skills TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Active'
            );
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                department TEXT NOT NULL,
                applicants INTEGER NOT NULL,
                status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS applicants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                experience TEXT NOT NULL,
                skills TEXT NOT NULL,
                stage TEXT NOT NULL,
                match_score INTEGER NOT NULL DEFAULT 70
            );
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                section TEXT NOT NULL,
                content TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS attrition_predictions (
                employee_id INTEGER PRIMARY KEY,
                risk_score REAL NOT NULL,
                factors TEXT NOT NULL,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            );
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS learning_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                skill TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Planned',
                created_at TEXT NOT NULL,
                FOREIGN KEY(employee_id) REFERENCES employees(id)
            );
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_user_id INTEGER NOT NULL,
                actor_user_id INTEGER,
                event_type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                read_at TEXT,
                FOREIGN KEY(recipient_user_id) REFERENCES users(id),
                FOREIGN KEY(actor_user_id) REFERENCES users(id)
            );
            """
        )
        employee_columns = {row["name"] for row in db.execute("PRAGMA table_info(employees)").fetchall()}
        dataset_mode = "employee_id" in employee_columns
        if "fired_by" not in employee_columns:
            db.execute("ALTER TABLE employees ADD COLUMN fired_by TEXT")
        if "firing_reason" not in employee_columns:
            db.execute("ALTER TABLE employees ADD COLUMN firing_reason TEXT")
        ensure_dataset_compatibility(db)
        employee_count = db.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        if employee_count == 0:
            employees = [
                (1, "Rahul Mehta", "Backend Engineer", "Engineering", "Bengaluru", 2.4, 4.2, 2.4, 1, "Python, SQL, Django"),
                (2, "Maya Chen", "Product Designer", "Product", "Singapore", 4.8, 4.7, 4.5, 0, "Figma, Research, Prototyping"),
                (3, "Arjun Nair", "Support Lead", "Customer Success", "Mumbai", 6.1, 3.8, 2.9, 1, "Zendesk, Coaching, Analytics"),
                (4, "Sofia Williams", "Data Analyst", "Finance", "London", 1.7, 4.4, 3.8, 0, "Python, SQL, Tableau"),
                (5, "Diego Alvarez", "Frontend Engineer", "Engineering", "Madrid", 3.2, 4.0, 3.1, 1, "JavaScript, React, CSS"),
                (6, "Priya Shah", "HR Business Partner", "People", "Pune", 5.5, 4.6, 4.2, 0, "People Analytics, Coaching, Policy"),
            ]
            db.executemany(
                "INSERT INTO employees (id, name, role, department, location, tenure_years, performance_score, satisfaction_score, overtime, skills) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                employees,
            )
            db.executemany(
                "INSERT INTO jobs (id, title, department, applicants, status) VALUES (?, ?, ?, ?, ?)",
                [(1, "Senior Backend Engineer", "Engineering", 18, "Interviewing"), (2, "People Operations Manager", "People", 11, "Screening"), (3, "Product Researcher", "Product", 7, "New")],
            )
            db.executemany(
                "INSERT INTO applicants (name, role, experience, skills, stage, match_score) VALUES (?, ?, ?, ?, ?, ?)",
                [("Anika Rao", "Senior Backend Engineer", "6 years", "Python, Django, AWS", "Interviewing", 94), ("Marcus Lee", "Senior Backend Engineer", "5 years", "Go, SQL, Docker", "Screening", 87), ("Nora Patel", "People Operations Manager", "8 years", "People Ops, Analytics, Policy", "New", 91), ("Owen Smith", "Product Researcher", "4 years", "Research, Interviews, Figma", "Screening", 78)],
            )
            db.executemany(
                "INSERT INTO policies (id, title, section, content) VALUES (?, ?, ?, ?)",
                [
                    (1, "Leave Policy", "Section 4.2", "Employees may carry forward up to 5 unused casual leave days into the following calendar year. Carry-forward requests must be recorded by January 31."),
                    (2, "Remote Work Policy", "Section 2.1", "Eligible employees may work remotely up to three days per week with manager approval and team coverage."),
                    (3, "Learning & Development", "Section 6.3", "Employees receive an annual learning allowance of 1,200 credits for approved courses, certifications, and conferences."),
                ],
            )
        if db.execute("SELECT COUNT(*) FROM policies").fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO policies (id, title, section, content) VALUES (?, ?, ?, ?)",
                [
                    (1, "Leave Policy", "Section 4.2", "Employees may carry forward up to 5 unused casual leave days into the following calendar year. Carry-forward requests must be recorded by January 31."),
                    (2, "Remote Work Policy", "Section 2.1", "Eligible employees may work remotely up to three days per week with manager approval and team coverage."),
                    (3, "Learning & Development", "Section 6.3", "Employees receive an annual learning allowance of 1,200 credits for approved courses, certifications, and conferences."),
                ],
            )
        applicant_seeds = [
            ("Anika Rao", "Senior Backend Engineer", "6 years", "Python, Django, AWS", "Interviewing", 94),
            ("Marcus Lee", "Senior Backend Engineer", "5 years", "Go, SQL, Docker", "Screening", 87),
            ("Nora Patel", "People Operations Manager", "8 years", "People Ops, Analytics, Policy", "New", 91),
            ("Owen Smith", "Product Researcher", "4 years", "Research, Interviews, Figma", "Screening", 78),
        ]
        if not dataset_mode:
            for candidate in applicant_seeds:
                exists = db.execute("SELECT 1 FROM applicants WHERE name = ?", (candidate[0],)).fetchone()
                if not exists:
                    db.execute("INSERT INTO applicants (name, role, experience, skills, stage, match_score) VALUES (?, ?, ?, ?, ?, ?)", candidate)
        now = datetime.now(timezone.utc).isoformat()
        if os.getenv("VERCEL"):
            admin_email = os.getenv("HR_ADMIN_EMAIL")
            admin_password = os.getenv("HR_ADMIN_PASSWORD")
            if not admin_email or not admin_password:
                raise RuntimeError("Set HR_ADMIN_EMAIL and HR_ADMIN_PASSWORD in Vercel project settings")
            default_users = [("PeopleOS Admin", admin_email, admin_password, "HR Admin")]
        else:
            default_users = [
                ("Priya Shah", os.getenv("HR_ADMIN_EMAIL", "hr@peopleos.local"), os.getenv("HR_ADMIN_PASSWORD", "PeopleOS2026!"), "HR Business Partner"),
                ("PeopleOS Admin", "admin@peopleos.local", "PeopleOSAdmin2026!", "HR Admin"),
            ]
        for name, email, password, role in default_users:
            exists = db.execute("SELECT 1 FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()
            if not exists:
                db.execute("INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)", (name, email, password_hash(password), role, now))
        db.commit()


def calculate_risk(employee: sqlite3.Row) -> tuple[float, list[str]]:
    analysis = analyze_employee(employee)
    return analysis["retention_risk"], analysis["factors"]


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def analyze_employee(employee: sqlite3.Row) -> dict[str, Any]:
    """Calculate explainable workforce scores from stored employee attributes only."""
    skills = [skill.strip().lower() for skill in employee["skills"].split(",") if skill.strip()]
    skill_count = len(skills)
    seed_text = f"{employee['id']}:{employee['name']}:{employee['role']}"
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:8], 16)
    variation = random.Random(seed)
    noise = variation.uniform(-0.035, 0.035)
    performance = employee["performance_score"] / 5
    satisfaction = employee["satisfaction_score"] / 5
    tenure = clamp(employee["tenure_years"] / 6)
    skill_breadth = clamp(skill_count / 5)
    overtime_load = 1.0 if employee["overtime"] else 0.18
    factors: list[str] = []
    if employee["satisfaction_score"] < 3.2:
        factors.append("low satisfaction")
    if employee["overtime"]:
        factors.append("sustained overtime")
    if employee["tenure_years"] < 2:
        factors.append("early tenure")
    if employee["performance_score"] < 4.0:
        factors.append("performance trend")

    retention_risk = clamp(
        0.08 + (1 - satisfaction) * 0.42 + overtime_load * 0.18 + (1 - tenure) * 0.12 + (1 - performance) * 0.16 + noise * 0.45
    )
    engagement = clamp(satisfaction * 0.52 + performance * 0.28 + (1 - overtime_load) * 0.12 + skill_breadth * 0.08 + noise)
    growth_readiness = clamp(performance * 0.42 + satisfaction * 0.24 + tenure * 0.18 + skill_breadth * 0.16 + noise)
    workload_index = clamp(overtime_load * 0.52 + (1 - satisfaction) * 0.28 + performance * 0.12 + noise)
    return {
        "retention_risk": round(retention_risk, 2),
        "engagement_score": round(engagement * 100),
        "growth_readiness": round(growth_readiness * 100),
        "workload_index": round(workload_index * 100),
        "skills_count": skill_count,
        "factors": factors,
    }


def build_skill_gaps(employees: list[sqlite3.Row]) -> list[dict[str, Any]]:
    required_by_group = {
        "Engineering": ["Docker", "AWS", "System Design", "Testing"],
        "Product": ["Research", "Analytics", "Prototyping", "Stakeholder Management"],
        "People": ["People Analytics", "Coaching", "Policy", "Data"],
        "Finance": ["SQL", "Tableau", "Python", "Data Storytelling"],
        "Customer Success": ["Analytics", "Coaching", "Leadership", "Customer Research"],
    }
    coverage: dict[str, list[int]] = {}
    for employee in employees:
        employee_skills = " ".join(employee["skills"].lower().split())
        required = required_by_group.get(employee["department"], ["Communication", "Analytics", "Planning"])
        for skill in required:
            coverage.setdefault(skill, []).append(100 if skill.lower() in employee_skills else 0)
    gaps = []
    for skill, values in coverage.items():
        current = round(sum(values) / len(values))
        required = 72
        gaps.append({"skill": skill, "current": current, "required": required, "gap": max(required - current, 0)})
    return sorted(gaps, key=lambda item: item["gap"], reverse=True)[:6]


def performance_detail(employee_id: int) -> dict[str, Any]:
    with closing(connect()) as db:
        employee = db.execute(
            "SELECT * FROM employees WHERE id = ?", (employee_id,)
        ).fetchone()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        normalized_id = employee["employee_id"]
        history = db.execute(
            """
            SELECT period_start, period_end, overall_score, previous_score,
                   score_change, trend_percentage, kpi_score, feedback_score,
                   goal_score, skill_score
            FROM employee_performance_history
            WHERE employee_id = ?
            ORDER BY period_start
            """,
            (normalized_id,),
        ).fetchall()
        latest = history[-1] if history else None
        kpis = db.execute(
            """
            SELECT k.kpi_name, k.description, rk.weight, rk.target_value,
                   rk.minimum_value, rk.maximum_value, rk.measurement_type,
                   rk.direction, r.actual_value, r.normalized_score,
                   r.data_source, r.period_start, r.period_end
            FROM employee_kpi_records r
            INNER JOIN role_kpis rk ON rk.role_kpi_id = r.role_kpi_id
            INNER JOIN kpis k ON k.kpi_id = rk.kpi_id
            WHERE r.employee_id = ?
              AND r.period_end = COALESCE(?, (SELECT MAX(period_end) FROM employee_kpi_records WHERE employee_id = ?))
            ORDER BY rk.weight DESC, k.kpi_name
            """,
            (normalized_id, latest["period_end"] if latest else None, normalized_id),
        ).fetchall()
        feedback = db.execute(
            """
            SELECT reviewer_role, overall_rating, comment, period
            FROM employee_feedback
            WHERE employee_id = ?
            ORDER BY period DESC
            LIMIT 12
            """,
            (normalized_id,),
        ).fetchall()
        skills = db.execute(
            """
            SELECT s.skill_id, COALESCE(c.training_name, s.skill_id) AS skill_name,
                   s.proficiency_level, s.proficiency_score
            FROM employee_skills s
            LEFT JOIN skill_training_catalog c ON c.skill_id = s.skill_id
            WHERE s.employee_id = ?
            GROUP BY s.skill_id
            ORDER BY s.proficiency_score DESC
            """,
            (normalized_id,),
        ).fetchall()
        role = db.execute(
            "SELECT role_name FROM roles WHERE role_id = (SELECT role_id FROM employees WHERE employee_id = ?)",
            (normalized_id,),
        ).fetchone()
        manager = db.execute("SELECT name FROM employees WHERE id = ?", (employee["manager_id"],)).fetchone()
        role_name = role["role_name"] if role else employee["role"]
        occupation_aliases = {
            "Backend Developer": "Software Developers",
            "Frontend Developer": "Web Developers",
            "DevOps Engineer": "Computer Systems Analysts",
            "QA Engineer": "Software Developers",
            "Support Specialist": "Customer Service Representatives",
            "System Administrator": "Computer Systems Analysts",
            "Security Analyst": "Information Security Analysts",
        }
        occupation_search = occupation_aliases.get(role_name, role_name)
        occupation = db.execute(
            "SELECT occupation_code, occupation_title FROM onet_occupations WHERE lower(occupation_title) LIKE ? ORDER BY occupation_title LIMIT 1",
            (f"%{occupation_search.lower()}%",),
        ).fetchone()
        required_skills = []
        if occupation:
            required_skills = db.execute(
                """
                SELECT DISTINCT os.element_name
                FROM onet_occupation_skills os
                WHERE os.occupation_code = ?
                ORDER BY os.data_value DESC
                LIMIT 6
                """,
                (occupation["occupation_code"],),
            ).fetchall()
        training = db.execute(
            """
            SELECT DISTINCT c.training_name, c.skill_id, c.provider, c.duration_hours
            FROM skill_training_catalog c
            WHERE c.skill_id IN (
                SELECT skill_id FROM employee_skills WHERE employee_id = ?
            )
            LIMIT 6
            """,
            (normalized_id,),
        ).fetchall()

    current_skills = {str(row["skill_name"]).lower() for row in skills}
    gaps = []
    for required in required_skills:
        skill_name = required["element_name"]
        if skill_name.lower() not in current_skills:
            gaps.append({
                "skill": skill_name,
                "current_level": "Not assessed",
                "required_level": "Role reference",
                "recommended_training": f"Build {skill_name} capability through role-aligned practice and training.",
            })
    breakdown = []
    for row in kpis:
        weight = float(row["weight"] or 0)
        score = float(row["normalized_score"] or 0)
        breakdown.append({
            "kpi": row["kpi_name"],
            "actual": row["actual_value"],
            "target": row["target_value"],
            "score": round(score, 2),
            "weight": round(weight * 100, 2),
            "contribution": round(score * weight, 2),
            "direction": row["direction"],
            "measurement_type": row["measurement_type"],
            "data_source": row["data_source"],
        })
    weighted_score = sum(item["contribution"] for item in breakdown)
    latest_score = round(weighted_score, 2) if breakdown else (float(latest["overall_score"] or 0) if latest else float(employee["performance_score"] or 0) * 20)
    previous_score = float(latest["previous_score"] or 0) if latest else 0
    strengths = [item["kpi"] for item in breakdown if item["score"] >= 80][:3]
    if not strengths:
        strengths = ["Structured performance evidence is available for review."]
    development = gaps[:4] or [{"skill": "No O*NET gap matched", "current_level": "Review current role needs", "required_level": "Role reference", "recommended_training": "Review role KPI evidence and recent feedback."}]
    feedback_analysis = ai_service.analyze_feedback([row["comment"] for row in feedback])
    evidence = [
        {"period": row["period_start"], "score": row["overall_score"]}
        for row in history
    ]
    return {
        "employee": {"id": employee["id"], "name": employee["name"], "role": role_name, "department": employee["department"], "manager_id": employee["manager_id"], "manager_name": manager["name"] if manager else "Not assigned"},
        "current_score": round(latest_score, 2),
        "previous_score": round(previous_score, 2),
        "score_change": round(float(latest["score_change"] or 0), 2) if latest else 0,
        "trend_percentage": round(float(latest["trend_percentage"] or 0), 2) if latest else 0,
        "history": evidence,
        "kpi_breakdown": breakdown,
        "feedback": [dict(row) for row in feedback],
        "feedback_analysis": feedback_analysis,
        "strengths": strengths,
        "development_areas": development,
        "skills": [dict(row) for row in skills[:12]],
        "training": [dict(row) for row in training],
        "explainability": "Overall score is the stored weighted result of the role's normalized objective KPI records. Feedback is shown as supporting evidence and does not replace the objective score.",
    }


def normalize_resume_name(name: str | None) -> tuple[str, str]:
    candidate_name = re.sub(r"\s+", " ", (name or "")).strip()
    if not candidate_name:
        return "Unknown", "Candidate"
    parts = candidate_name.split()
    if len(parts) == 1:
        return parts[0], "Candidate"
    return parts[0], " ".join(parts[1:])


def derive_candidate_from_resume(extraction: dict[str, Any], candidate_id: str | None = None) -> dict[str, Any]:
    first_name, last_name = normalize_resume_name(extraction.get("name"))
    experience_items = extraction.get("experience") or []
    role = None
    total_years = None
    for item in experience_items:
        if isinstance(item, dict):
            title = item.get("title") or item.get("role")
            if title and not role:
                role = title
            duration = str(item.get("duration") or item.get("years") or "")
            match = re.search(r"(\d+(?:\.\d+)?)", duration)
            if match and total_years is None:
                total_years = float(match.group(1))
    education_items = extraction.get("education") or []
    education = None
    if education_items and isinstance(education_items[0], dict):
        education = education_items[0].get("degree") or education_items[0].get("field")
    email = (extraction.get("email") or "").strip() or (f"resume.{candidate_id.lower()}@peopleos.local" if candidate_id else "resume@peopleos.local")
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "location": (extraction.get("location") or "").strip() or None,
        "current_role": role or None,
        "total_experience_years": total_years,
        "highest_education": education or None,
        "education_field": None,
    }


def sync_applicant_record(db: sqlite3.Connection, candidate_id: str) -> None:
    candidate = db.execute(
        "SELECT first_name, last_name, current_role, total_experience_years, email, location FROM candidates WHERE candidate_id = ?",
        (candidate_id,),
    ).fetchone()
    if not candidate:
        return
    applicant_id = int(candidate_id[3:]) if candidate_id.startswith("CAN") and candidate_id[3:].isdigit() else None
    name = f"{candidate['first_name'] or ''} {candidate['last_name'] or ''}".strip() or "Candidate"
    role = candidate["current_role"] or "Candidate"
    experience = f"{candidate['total_experience_years'] or 0:g} years" if candidate["total_experience_years"] is not None else "Not stated"
    if applicant_id is not None:
        existing = db.execute("SELECT id FROM applicants WHERE id = ?", (applicant_id,)).fetchone()
        if existing:
            db.execute(
                "UPDATE applicants SET name = ?, role = ?, experience = ?, skills = COALESCE(skills, 'Resume pending analysis'), match_score = COALESCE(match_score, 0) WHERE id = ?",
                (name, role, experience, applicant_id),
            )
            return
    db.execute(
        "INSERT INTO applicants (id, name, role, experience, skills, stage, match_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (applicant_id if applicant_id is not None else db.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM applicants").fetchone()[0], name, role, experience, "Resume pending analysis", "New", 0),
    )


def candidate_name(db: sqlite3.Connection, candidate_id: str) -> str:
    row = db.execute("SELECT first_name || ' ' || last_name AS name FROM candidates WHERE candidate_id = ?", (candidate_id,)).fetchone()
    return row["name"] if row else candidate_id


def candidate_detail(db: sqlite3.Connection, candidate_id: str) -> dict[str, Any]:
    candidate = db.execute("SELECT * FROM candidates WHERE candidate_id = ?", (candidate_id,)).fetchone()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    skills = db.execute(
        """
        SELECT cs.*, COALESCE(os.element_name, cs.skill_id) AS skill_name
        FROM candidate_skills cs
        LEFT JOIN onet_skills os ON os.element_id = cs.skill_id
        WHERE cs.candidate_id = ? ORDER BY cs.proficiency_score DESC
        """, (candidate_id,)
    ).fetchall()
    experience = db.execute("SELECT * FROM candidate_experience WHERE candidate_id = ? ORDER BY start_date DESC", (candidate_id,)).fetchall()
    education = db.execute("SELECT * FROM candidate_education WHERE candidate_id = ? ORDER BY end_year DESC", (candidate_id,)).fetchall()
    certifications = db.execute("SELECT * FROM candidate_certifications WHERE candidate_id = ? ORDER BY issue_date DESC", (candidate_id,)).fetchall()
    projects = db.execute("SELECT * FROM candidate_projects WHERE candidate_id = ? ORDER BY duration_months DESC", (candidate_id,)).fetchall()
    evidence = db.execute("SELECT * FROM candidate_evidence WHERE candidate_id = ? ORDER BY confidence_score DESC", (candidate_id,)).fetchall()
    resume = next((row for row in evidence if row["evidence_type"] == "resume"), None)
    extraction_row = db.execute("SELECT extraction_json FROM candidate_resume_extractions WHERE candidate_id = ? ORDER BY created_at DESC LIMIT 1", (candidate_id,)).fetchone()
    scores = db.execute(
        """
        SELECT s.*, j.job_title FROM candidate_job_scores s
        INNER JOIN jobs j ON j.job_id = s.job_id
        WHERE s.candidate_id = ? ORDER BY s.overall_match_score DESC
        """, (candidate_id,)
    ).fetchall()
    return {
        "candidate": dict(candidate),
        "name": candidate_name(db, candidate_id),
        "skills": [dict(row) for row in skills],
        "experience": [dict(row) for row in experience],
        "education": [dict(row) for row in education],
        "certifications": [dict(row) for row in certifications],
        "projects": [dict(row) for row in projects],
        "evidence": [dict(row) for row in evidence],
        "resume_extraction": json.loads(extraction_row["extraction_json"]) if extraction_row else ai_service.extract_resume_profile(resume["source_text"] if resume else ""),
        "job_scores": [dict(row) for row in scores],
    }


def calculate_candidate_match(db: sqlite3.Connection, candidate_id: str, job_id: str) -> dict[str, Any]:
    candidate = db.execute("SELECT * FROM candidates WHERE candidate_id = ?", (candidate_id,)).fetchone()
    job = db.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    if not candidate or not job:
        raise HTTPException(status_code=404, detail="Candidate or job not found")
    requirements = db.execute(
        """
        SELECT jr.*, COALESCE(os.element_name, jr.skill_id) AS skill_name
        FROM job_requirements jr LEFT JOIN onet_skills os ON os.element_id = jr.skill_id
        WHERE jr.job_id = ? ORDER BY jr.is_mandatory DESC, jr.weight DESC
        """, (job_id,)
    ).fetchall()
    candidate_skills = {row["skill_id"]: row for row in db.execute("SELECT * FROM candidate_skills WHERE candidate_id = ?", (candidate_id,)).fetchall()}
    weighted_matches = []
    mandatory_met = 0
    mandatory_failed = 0
    for requirement in requirements:
        skill = candidate_skills.get(requirement["skill_id"])
        direct_match = 100 if skill else 0
        proficiency = min(100, round(float(skill["proficiency_score"] or 0) / max(float(requirement["required_proficiency_score"] or 100), 1) * 100)) if skill else 0
        weight = float(requirement["weight"] or 0)
        weighted_matches.append((direct_match, proficiency, weight))
        if requirement["is_mandatory"]:
            if skill and proficiency >= 80:
                mandatory_met += 1
            else:
                mandatory_failed += 1
    total_weight = sum(item[2] for item in weighted_matches) or 1
    skill_score = round(sum(item[0] * item[2] for item in weighted_matches) / total_weight, 2)
    proficiency_score = round(sum(item[1] * item[2] for item in weighted_matches) / total_weight, 2)
    minimum_years = float(job["minimum_experience_years"] or 0)
    experience_score = min(100, round(float(candidate["total_experience_years"] or 0) / minimum_years * 100, 2)) if minimum_years else 100
    projects = db.execute("SELECT * FROM candidate_projects WHERE candidate_id = ?", (candidate_id,)).fetchall()
    project_text = " ".join(f"{row['technologies'] or ''} {row['description'] or ''}" for row in projects).lower()
    job_text = f"{job['job_title']} {job['job_description'] or ''}".lower()
    project_relevance = round(min(100, 50 + 10 * sum(token in project_text for token in set(re.findall(r"[a-z0-9]+", job_text)) if len(token) > 4)), 2) if projects else 0
    answers = db.execute("SELECT * FROM interview_answers WHERE candidate_id = ?", (candidate_id,)).fetchall()
    interview_score = round(sum(float(row["technical_correctness"] or 0) + float(row["conceptual_understanding"] or 0) + float(row["practical_reasoning"] or 0) + float(row["communication"] or 0) for row in answers) / max(len(answers) * 4, 1), 2)
    problem_solving = round(sum(float(row["problem_solving"] or 0) for row in answers) / max(len(answers), 1), 2)
    education_score = 100 if db.execute("SELECT 1 FROM candidate_education WHERE candidate_id = ?", (candidate_id,)).fetchone() else 0
    overall = round(skill_score * .30 + proficiency_score * .15 + experience_score * .15 + project_relevance * .10 + interview_score * .15 + problem_solving * .10 + education_score * .05, 2)
    match_id = f"MATCH_{candidate_id}_{job_id}"
    values = (match_id, candidate_id, job_id, skill_score, proficiency_score, experience_score, project_relevance, interview_score, problem_solving, education_score, overall, mandatory_met, mandatory_failed, "deterministic-v1", datetime.now(timezone.utc).isoformat())
    existing = db.execute("SELECT 1 FROM candidate_job_scores WHERE candidate_id = ? AND job_id = ?", (candidate_id, job_id)).fetchone()
    if existing:
        db.execute("""UPDATE candidate_job_scores SET required_skill_score=?, skill_proficiency_score=?, experience_score=?, project_relevance_score=?, interview_score=?, problem_solving_score=?, education_score=?, overall_match_score=?, mandatory_requirements_met=?, mandatory_requirements_failed=?, calculation_version=?, calculated_at=? WHERE candidate_id=? AND job_id=?""", values[3:] + values[1:3])
    else:
        db.execute("INSERT INTO candidate_job_scores (match_id, candidate_id, job_id, required_skill_score, skill_proficiency_score, experience_score, project_relevance_score, interview_score, problem_solving_score, education_score, overall_match_score, mandatory_requirements_met, mandatory_requirements_failed, calculation_version, calculated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
    db.commit()
    return {
        "candidate_id": candidate_id, "job_id": job_id, "overall_match_score": overall,
        "components": {"required_skill_match": skill_score, "skill_proficiency": proficiency_score, "experience": experience_score, "projects": project_relevance, "interview": interview_score, "problem_solving": problem_solving, "education": education_score},
        "mandatory": {"met": mandatory_met, "failed": mandatory_failed, "status": "passed" if mandatory_failed == 0 else "failed"},
        "requirements": [{"skill": row["skill_name"], "required_proficiency": row["required_proficiency"], "candidate_found": row["skill_id"] in candidate_skills, "match": 100 if row["skill_id"] in candidate_skills else 0, "evidence": candidate_skills[row["skill_id"]]["evidence_text"] if row["skill_id"] in candidate_skills else "Not found in submitted evidence"} for row in requirements],
        "explainability": "This score is a deterministic candidate-to-job assessment. It is not a guaranteed hiring decision.",
    }


def extract_resume_text(content: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".txt", ".md"}:
        return content.decode("utf-8", errors="ignore")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader

            return "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)
        except ImportError as error:
            raise HTTPException(status_code=500, detail="PDF resume support is not installed") from error
    if suffix == ".docx":
        try:
            from docx import Document

            return "\n".join(paragraph.text for paragraph in Document(BytesIO(content)).paragraphs)
        except ImportError as error:
            raise HTTPException(status_code=500, detail="DOCX resume support is not installed") from error
    raise HTTPException(status_code=415, detail="Resume must be PDF, DOCX, or TXT")


def persist_resume_profile(db: sqlite3.Connection, candidate_id: str, filename: str, extraction: dict[str, Any]) -> None:
    extraction_id = f"EXTRACT_{candidate_id}_{int(datetime.now().timestamp())}"
    db.execute(
        "INSERT INTO candidate_resume_extractions (extraction_id, candidate_id, source_document, extraction_json, extraction_status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (extraction_id, candidate_id, filename, json.dumps(extraction), extraction.get("evidence_status", "not_found"), datetime.now(timezone.utc).isoformat()),
    )
    name = (extraction.get("name") or "").strip()
    if name:
        parts = name.split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        db.execute(
            "UPDATE candidates SET first_name = COALESCE(NULLIF(first_name, ''), ?), last_name = COALESCE(NULLIF(last_name, ''), ?) WHERE candidate_id = ?",
            (first_name, last_name, candidate_id),
        )
    email = (extraction.get("email") or "").strip()
    if email:
        db.execute("UPDATE candidates SET email = COALESCE(NULLIF(email, ''), ?) WHERE candidate_id = ?", (email, candidate_id))
    location = (extraction.get("location") or "").strip()
    if location:
        db.execute("UPDATE candidates SET location = COALESCE(NULLIF(location, ''), ?) WHERE candidate_id = ?", (location, candidate_id))
    role = (extraction.get("current_role") or extraction.get("role") or "").strip() or None
    if role:
        db.execute("UPDATE candidates SET current_role = COALESCE(NULLIF(current_role, ''), ?) WHERE candidate_id = ?", (role, candidate_id))
    catalog = db.execute("SELECT skill_id, training_name FROM skill_training_catalog").fetchall()
    for index, item in enumerate(extraction.get("skills") or []):
        if not isinstance(item, dict) or not item.get("name"):
            continue
        name = str(item["name"]).strip()
        match = next((row for row in catalog if name.lower() in row["training_name"].lower() or row["training_name"].lower() in name.lower()), None)
        skill_id = match["skill_id"] if match else f"RESUME_{candidate_id}_{index:03d}"
        proficiency = item.get("proficiency") or "not_stated"
        try:
            confidence = float(item.get("confidence") or 0)
        except (TypeError, ValueError):
            confidence = 0.0
        db.execute(
            "INSERT OR REPLACE INTO candidate_skills (candidate_skill_id, candidate_id, skill_id, proficiency_level, proficiency_score, years_experience, evidence_text, evidence_source, confidence_score, verification_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"EXTRACT_{candidate_id}_SKILL_{index}", candidate_id, skill_id, proficiency, 0, 0, item.get("evidence") or f"Found in uploaded resume: {name}", "resume", confidence, "unverified"),
        )
    for index, item in enumerate(extraction.get("experience") or []):
        if not isinstance(item, dict):
            continue
        duration = str(item.get("duration") or item.get("years") or "not_found")
        duration_match = re.search(r"\d+(?:\.\d+)?", duration)
        db.execute(
            "INSERT OR REPLACE INTO candidate_experience (experience_id, candidate_id, company, job_title, start_date, duration_months, description, technologies, domain) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"EXTRACT_{candidate_id}_EXP_{index}", candidate_id, item.get("company") or "not_found", item.get("title") or item.get("role") or "not_found", "1900-01-01", round(float(duration_match.group()) * 12) if duration_match else None, item.get("description") or "not_found", ", ".join(item.get("technologies") or []) if isinstance(item.get("technologies"), list) else item.get("technologies") or "not_found", item.get("domain") or "not_found"),
        )
    for index, item in enumerate(extraction.get("projects") or []):
        if not isinstance(item, dict):
            continue
        technologies = item.get("technologies") or []
        db.execute(
            "INSERT OR REPLACE INTO candidate_projects (candidate_project_id, candidate_id, project_name, description, role, technologies, domain, duration_months, complexity, outcome, evidence_source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"EXTRACT_{candidate_id}_PROJ_{index}", candidate_id, item.get("name") or "not_found", item.get("description") or "not_found", item.get("role") or "not_found", ", ".join(technologies) if isinstance(technologies, list) else technologies or "not_found", item.get("domain") or "not_found", None, item.get("complexity") or "not_stated", item.get("outcome") or "not_stated", "resume"),
        )
    for index, item in enumerate(extraction.get("education") or []):
        if not isinstance(item, dict):
            continue
        year_match = re.search(r"\b(19|20)\d{2}\b", str(item.get("year") or ""))
        end_year = int(year_match.group()) if year_match else None
        db.execute(
            "INSERT OR REPLACE INTO candidate_education (education_id, candidate_id, degree, field, institution, end_year, education_level) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (f"EXTRACT_{candidate_id}_EDU_{index}", candidate_id, item.get("degree") or "not_found", item.get("field") or "not_found", item.get("institution") or "not_found", end_year, item.get("level") or item.get("degree") or "not_stated"),
        )
    for index, item in enumerate(extraction.get("certifications") or []):
        if not isinstance(item, dict):
            continue
        db.execute(
            "INSERT OR REPLACE INTO candidate_certifications (certification_id, candidate_id, certification_name, issuing_organization, verification_status, related_skill_id) VALUES (?, ?, ?, ?, ?, ?)",
            (f"EXTRACT_{candidate_id}_CERT_{index}", candidate_id, item.get("name") or item.get("certification") or "not_found", item.get("organization") or "not_found", "unverified", item.get("skill_id")),
        )
    first_experience = next((item for item in (extraction.get("experience") or []) if isinstance(item, dict)), None)
    total_months = 0
    for item in extraction.get("experience") or []:
        if isinstance(item, dict):
            duration_match = re.search(r"\d+(?:\.\d+)?", str(item.get("duration") or item.get("years") or ""))
            if duration_match:
                total_months += round(float(duration_match.group()) * 12)
    if first_experience:
        role = first_experience.get("title") or first_experience.get("role")
        if role:
            db.execute("UPDATE candidates SET current_role = COALESCE(NULLIF(current_role, ''), ?) WHERE candidate_id = ?", (role, candidate_id))
    first_education = next((item for item in (extraction.get("education") or []) if isinstance(item, dict)), None)
    if first_education:
        db.execute(
            "UPDATE candidates SET highest_education = COALESCE(NULLIF(highest_education, ''), ?), education_field = COALESCE(NULLIF(education_field, ''), ?) WHERE candidate_id = ?",
            (first_education.get("degree") or None, first_education.get("field") or None, candidate_id),
        )
    if total_months:
        db.execute("UPDATE candidates SET total_experience_years = COALESCE(total_experience_years, ?) WHERE candidate_id = ?", (round(total_months / 12, 1), candidate_id))
    applicant_id = int(candidate_id[3:]) if candidate_id.startswith("CAN") and candidate_id[3:].isdigit() else None
    if applicant_id is not None:
        skills = [str(item.get("name")) for item in (extraction.get("skills") or []) if isinstance(item, dict) and item.get("name")]
        role = db.execute("SELECT current_role FROM candidates WHERE candidate_id = ?", (candidate_id,)).fetchone()["current_role"]
        experience = db.execute("SELECT total_experience_years FROM candidates WHERE candidate_id = ?", (candidate_id,)).fetchone()["total_experience_years"]
        db.execute("UPDATE applicants SET skills = ?, role = COALESCE(?, role), experience = ? WHERE id = ?", (", ".join(skills) or "Resume analyzed", role, f"{experience:g} years" if experience is not None else "Not stated", applicant_id))
    else:
        sync_applicant_record(db, candidate_id)


@app.on_event("startup")
def startup() -> None:
    if os.getenv("VERCEL"):
        with closing(connect()) as db:
            initialized = db.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'candidates'").fetchone()
        if not initialized:
            if DB_PATH.exists():
                DB_PATH.unlink()
            from Database.seed_database import DatabaseAdapter, seed_database as seed_dataset

            dataset_db = DatabaseAdapter("sqlite", sqlite_path=str(DB_PATH))
            try:
                dataset_db.connect()
                seed_dataset(dataset_db)
            finally:
                dataset_db.close()
    seed_database()
    with closing(connect()) as db:
        prune_notifications(db)
        db.commit()


def require_session(token: str | None, admin: bool = False) -> sqlite3.Row:
    if not token:
        raise HTTPException(status_code=401, detail="HR login required")
    with closing(connect()) as db:
        user = db.execute("SELECT id, name, email, role, active FROM users INNER JOIN sessions ON sessions.user_id = users.id WHERE sessions.token = ?", (token,)).fetchone()
    if not user or not user["active"] or (admin and user["role"] != "HR Admin"):
        raise HTTPException(status_code=403 if admin else 401, detail="Admin access required" if admin else "HR login required")
    return user


def prune_notifications(db: sqlite3.Connection) -> None:
    db.execute("DELETE FROM notifications WHERE expires_at <= ?", (datetime.now(timezone.utc).isoformat(),))


def notify_activity(
    db: sqlite3.Connection,
    actor: sqlite3.Row | None,
    event_type: str,
    title: str,
    message: str,
    notify_hr: bool = False,
) -> None:
    now = datetime.now(timezone.utc)
    recipients = db.execute("SELECT id, role FROM users WHERE active = 1 AND (role = 'HR Admin' OR (? = 1 AND role != 'HR Admin'))", (1 if notify_hr else 0,)).fetchall()
    expires_at = (now + timedelta(days=30)).isoformat()
    for recipient in recipients:
        if actor and recipient["id"] == actor["id"] and recipient["role"] == "HR Admin":
            continue
        db.execute("INSERT INTO notifications (recipient_user_id, actor_user_id, event_type, title, message, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (recipient["id"], actor["id"] if actor else None, event_type, title, message, now.isoformat(), expires_at))


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "peopleos"}


@app.get("/api/options")
def options(token: str | None = None) -> dict[str, Any]:
    with closing(connect()) as db:
        departments = [row["department"] for row in db.execute("SELECT DISTINCT department FROM employees UNION SELECT DISTINCT department FROM jobs ORDER BY department").fetchall()]
        job_titles = [row["title"] for row in db.execute("SELECT DISTINCT title FROM jobs ORDER BY title").fetchall()]
    return {"roles": sorted(ROLE_OPTIONS - {"HR Admin"}), "admin_roles": sorted(ROLE_OPTIONS), "job_statuses": sorted(JOB_STATUS_OPTIONS), "departments": departments, "job_titles": job_titles}


@app.get("/api/notifications")
def notifications(token: str | None = None) -> dict[str, Any]:
    user = require_session(token)
    with closing(connect()) as db:
        prune_notifications(db)
        rows = db.execute("SELECT notifications.id, notifications.event_type, notifications.title, notifications.message, notifications.created_at, notifications.read_at, users.name AS actor_name FROM notifications LEFT JOIN users ON users.id = notifications.actor_user_id WHERE notifications.recipient_user_id = ? ORDER BY notifications.created_at DESC", (user["id"],)).fetchall()
        db.commit()
    return {"notifications": [dict(row) for row in rows], "unread_count": sum(row["read_at"] is None for row in rows)}


@app.post("/api/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, token: str | None = None) -> dict[str, bool]:
    user = require_session(token)
    with closing(connect()) as db:
        db.execute("UPDATE notifications SET read_at = ? WHERE id = ? AND recipient_user_id = ?", (datetime.now(timezone.utc).isoformat(), notification_id, user["id"]))
        db.commit()
    return {"ok": True}


@app.post("/api/notifications/read-all")
def mark_all_notifications_read(token: str | None = None) -> dict[str, bool]:
    user = require_session(token)
    with closing(connect()) as db:
        db.execute("UPDATE notifications SET read_at = ? WHERE recipient_user_id = ? AND read_at IS NULL", (datetime.now(timezone.utc).isoformat(), user["id"]))
        db.commit()
    return {"ok": True}


@app.post("/api/auth/login")
def login(credentials: LoginRequest) -> dict[str, str]:
    with closing(connect()) as db:
        user = db.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (credentials.email,)).fetchone()
    if not user or not user["active"] or user["password_hash"] != password_hash(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid HR credentials")
    token = secrets.token_urlsafe(24)
    with closing(connect()) as db:
        db.execute("INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)", (token, user["id"], datetime.now(timezone.utc).isoformat()))
        db.commit()
    return {"token": token, "name": user["name"], "role": user["role"], "is_admin": str(user["role"] == "HR Admin").lower()}


@app.post("/api/auth/logout")
def logout(token: str | None = None) -> dict[str, bool]:
    if token:
        with closing(connect()) as db:
            db.execute("DELETE FROM sessions WHERE token = ?", (token,))
            db.commit()
    return {"ok": True}


@app.post("/api/auth/register")
def register(request: RegistrationRequest) -> dict[str, Any]:
    if request.role not in ROLE_OPTIONS - {"HR Admin"}:
        raise HTTPException(status_code=400, detail="Choose a supported non-admin role")
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    try:
        with closing(connect()) as db:
            cursor = db.execute("INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)", (request.name, request.email.lower(), password_hash(request.password), request.role, datetime.now(timezone.utc).isoformat()))
            db.commit()
    except sqlite3.IntegrityError as error:
        raise HTTPException(status_code=409, detail="An account with that email already exists") from error
    return {"id": cursor.lastrowid, "name": request.name, "email": request.email.lower(), "role": request.role, "status": "Active"}


@app.get("/api/auth/me")
def current_user(token: str | None = None) -> dict[str, Any]:
    user = require_session(token)
    return dict(user)


@app.put("/api/auth/profile")
def update_profile(profile: ProfileUpdate, token: str | None = None) -> dict[str, Any]:
    user = require_session(token)
    if profile.password and profile.password != profile.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    try:
        with closing(connect()) as db:
            if profile.password:
                db.execute("UPDATE users SET name = ?, email = ?, password_hash = ? WHERE id = ?", (profile.name, profile.email.lower(), password_hash(profile.password), user["id"]))
            else:
                db.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (profile.name, profile.email.lower(), user["id"]))
            db.commit()
            updated = db.execute("SELECT id, name, email, role, active FROM users WHERE id = ?", (user["id"],)).fetchone()
            if user["role"] != "HR Admin":
                notify_activity(db, user, "profile_updated", "HR profile updated", f"{user['name']} updated their HR account profile.")
                db.commit()
    except sqlite3.IntegrityError as error:
        raise HTTPException(status_code=409, detail="An account with that email already exists") from error
    return dict(updated)


@app.get("/api/admin/users")
def admin_users(token: str | None = None) -> list[dict[str, Any]]:
    require_session(token, admin=True)
    with closing(connect()) as db:
        rows = db.execute("SELECT id, name, email, role, active, created_at FROM users ORDER BY id").fetchall()
    return [dict(row) for row in rows]


@app.post("/api/admin/users")
def admin_create_user(user: UserCreate, token: str | None = None) -> dict[str, Any]:
    require_session(token, admin=True)
    if user.role not in ROLE_OPTIONS:
        raise HTTPException(status_code=400, detail="Choose a supported role")
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    try:
        with closing(connect()) as db:
            cursor = db.execute("INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)", (user.name, user.email.lower(), password_hash(user.password), user.role, datetime.now(timezone.utc).isoformat()))
            db.commit()
    except sqlite3.IntegrityError as error:
        raise HTTPException(status_code=409, detail="An account with that email already exists") from error
    return {"id": cursor.lastrowid, "name": user.name, "email": user.email.lower(), "role": user.role, "active": 1}


@app.post("/api/admin/users/{user_id}/toggle")
def admin_toggle_user(user_id: int, token: str | None = None) -> dict[str, Any]:
    require_session(token, admin=True)
    with closing(connect()) as db:
        db.execute("UPDATE users SET active = CASE active WHEN 1 THEN 0 ELSE 1 END WHERE id = ?", (user_id,))
        db.commit()
        row = db.execute("SELECT id, name, email, role, active FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Account not found")
    return dict(row)


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    with closing(connect()) as db:
        employees = db.execute("SELECT * FROM employees ORDER BY id").fetchall()
        jobs = db.execute("SELECT * FROM jobs ORDER BY id").fetchall()
    analyses = []
    for employee in employees:
        analysis = analyze_employee(employee)
        analyses.append({"employee": employee, "analysis": analysis})
    risks = [{"employee_id": item["employee"]["id"], "name": item["employee"]["name"], "role": item["employee"]["role"], "risk_score": item["analysis"]["retention_risk"], "factors": item["analysis"]["factors"]} for item in analyses]
    average_performance = sum(employee["performance_score"] for employee in employees) / max(len(employees), 1)
    average_engagement = sum(item["analysis"]["engagement_score"] for item in analyses) / max(len(analyses), 1)
    performance_trend = [{"label": label, "value": round(clamp(average_performance + offset, 0, 5), 2)} for label, offset in (("Q1", -0.18), ("Q2", -0.08), ("Q3", 0.03), ("Q4", 0.08))]
    skill_gaps = build_skill_gaps(employees)
    return {
        "metrics": {"total_employees": len(employees), "active_employees": sum(e["status"] == "Active" for e in employees), "open_positions": len(jobs), "high_risk": sum(r["risk_score"] >= 0.55 for r in risks), "skill_gaps": sum(item["gap"] > 0 for item in skill_gaps), "average_performance": round(average_performance, 2), "average_engagement": round(average_engagement), "role_note": f"{len(jobs)} roles in progress", "risk_note": "Calculated from stored workforce signals", "skill_gap_note": f"{len(skill_gaps)} skills compared with role needs"},
        "risks": sorted(risks, key=lambda item: item["risk_score"], reverse=True),
        "jobs": [dict(job) for job in jobs],
        "performance": performance_trend,
    }


@app.get("/api/employees")
def employees() -> list[dict[str, Any]]:
    with closing(connect()) as db:
        rows = db.execute("SELECT * FROM employees ORDER BY name").fetchall()
    return [{**dict(row), **analyze_employee(row)} for row in rows]


@app.get("/api/employees/{employee_id}/performance")
def employee_performance(employee_id: int) -> dict[str, Any]:
    return performance_detail(employee_id)


@app.put("/api/employees/{employee_id}")
def update_employee(employee_id: int, employee: EmployeeUpdate, token: str | None = None) -> dict[str, Any]:
    actor = require_session(token)
    with closing(connect()) as db:
        existing = db.execute("SELECT id FROM employees WHERE id = ?", (employee_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Employee not found")
        db.execute("UPDATE employees SET name = ?, role = ?, department = ?, location = ?, skills = ?, performance_score = ?, satisfaction_score = ?, overtime = ? WHERE id = ?", (employee.name, employee.role, employee.department, employee.location, employee.skills, employee.performance_score, employee.satisfaction_score, employee.overtime, employee_id))
        notify_activity(db, actor, "employee_updated", "Employee details updated", f"{actor['name']} updated employee details for {employee.name}.")
        db.commit()
        row = db.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
    return {**dict(row), **analyze_employee(row)}


@app.post("/api/employees/{employee_id}/fire")
def fire_employee(employee_id: int, request: FireEmployeeRequest, token: str | None = None) -> dict[str, Any]:
    actor = require_session(token)
    with closing(connect()) as db:
        employee = db.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        db.execute("UPDATE employees SET status = 'Fired', fired_by = ?, firing_reason = ? WHERE id = ?", (actor["name"], request.reason, employee_id))
        notify_activity(db, actor, "employee_fired", "Employee status changed", f"{actor['name']} marked {employee['name']} as Fired.")
        db.commit()
        row = db.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
    return {**dict(row), **analyze_employee(row)}


@app.get("/api/recruitment")
def recruitment() -> dict[str, Any]:
    with closing(connect()) as db:
        jobs = [dict(row) for row in db.execute("SELECT * FROM jobs ORDER BY id").fetchall()]
        candidates = [dict(row) for row in db.execute("SELECT id, printf('CAN%03d', id) AS candidate_id, name, role, experience, skills, stage, match_score AS match FROM applicants WHERE stage NOT IN ('Hired', 'Rejected') ORDER BY match_score DESC").fetchall()]
    return {"jobs": jobs, "candidates": candidates}


@app.get("/api/jobs")
def jobs_data() -> list[dict[str, Any]]:
    with closing(connect()) as db:
        rows = db.execute("SELECT j.*, d.department_name AS department, r.role_name FROM jobs j LEFT JOIN departments d ON d.department_id = j.department_id LEFT JOIN roles r ON r.role_id = j.role_id ORDER BY j.created_date DESC, j.job_id").fetchall()
    return [dict(row) for row in rows]


@app.get("/api/jobs/{job_id}/requirements")
def job_requirements(job_id: str) -> list[dict[str, Any]]:
    with closing(connect()) as db:
        rows = db.execute("SELECT jr.*, COALESCE(os.element_name, jr.skill_id) AS skill_name FROM job_requirements jr LEFT JOIN onet_skills os ON os.element_id = jr.skill_id WHERE jr.job_id = ? ORDER BY jr.is_mandatory DESC, jr.weight DESC", (job_id,)).fetchall()
    return [dict(row) for row in rows]


@app.get("/api/jobs/{job_id}")
def job_data(job_id: str) -> dict[str, Any]:
    with closing(connect()) as db:
        job = db.execute("SELECT j.*, d.department_name AS department, r.role_name FROM jobs j LEFT JOIN departments d ON d.department_id = j.department_id LEFT JOIN roles r ON r.role_id = j.role_id WHERE j.job_id = ?", (job_id,)).fetchone()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"job": dict(job), "requirements": [dict(row) for row in db.execute("SELECT jr.*, COALESCE(os.element_name, jr.skill_id) AS skill_name FROM job_requirements jr LEFT JOIN onet_skills os ON os.element_id = jr.skill_id WHERE jr.job_id = ? ORDER BY jr.is_mandatory DESC, jr.weight DESC", (job_id,)).fetchall()]}


@app.post("/api/jobs/{job_id}/requirements")
def create_job_requirement(job_id: str, requirement: JobRequirementCreate, token: str | None = None) -> dict[str, Any]:
    require_session(token)
    with closing(connect()) as db:
        if not db.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Job not found")
        requirement_id = f"REQ_{job_id}_{requirement.skill_id}"
        db.execute("INSERT OR REPLACE INTO job_requirements (job_requirement_id, job_id, skill_id, required_proficiency, required_proficiency_score, weight, is_mandatory, requirement_type, minimum_years, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (requirement_id, job_id, requirement.skill_id, requirement.required_proficiency, requirement.required_proficiency_score, requirement.weight, requirement.is_mandatory, requirement.requirement_type, requirement.minimum_years, requirement.description))
        db.commit()
        row = db.execute("SELECT jr.*, COALESCE(os.element_name, jr.skill_id) AS skill_name FROM job_requirements jr LEFT JOIN onet_skills os ON os.element_id = jr.skill_id WHERE jr.job_requirement_id = ?", (requirement_id,)).fetchone()
    return dict(row)


@app.get("/api/candidates")
def candidates_data() -> list[dict[str, Any]]:
    with closing(connect()) as db:
        rows = db.execute("SELECT c.*, TRIM(c.first_name || ' ' || c.last_name) AS name, (SELECT COUNT(*) FROM candidate_job_scores s WHERE s.candidate_id = c.candidate_id) AS scored_jobs FROM candidates c ORDER BY c.application_date DESC, c.candidate_id").fetchall()
    return [dict(row) for row in rows]


@app.post("/api/candidates")
def create_candidate(candidate: CandidateCreate, token: str | None = None) -> dict[str, Any]:
    require_session(token)
    with closing(connect()) as db:
        next_number = db.execute("SELECT COALESCE(MAX(CAST(SUBSTR(candidate_id, 4) AS INTEGER)), 0) + 1 FROM candidates").fetchone()[0]
        candidate_id = f"CAN{int(next_number):03d}"
        try:
            db.execute("INSERT INTO candidates (candidate_id, candidate_code, first_name, last_name, email, location, total_experience_years, highest_education, education_field, current_role, application_date, source, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (candidate_id, f"C{int(next_number):03d}", candidate.first_name, candidate.last_name, candidate.email, candidate.location, candidate.total_experience_years, candidate.highest_education, candidate.education_field, candidate.current_role, datetime.now(timezone.utc).date().isoformat(), "direct", "applied"))
            sync_applicant_record(db, candidate_id)
            db.commit()
        except sqlite3.IntegrityError as error:
            raise HTTPException(status_code=409, detail="A candidate with this email already exists") from error
        return candidate_detail(db, candidate_id)


@app.post("/api/candidates/scan")
async def scan_candidate_resume(request: Request, token: str | None = None) -> dict[str, Any]:
    require_session(token)
    form = await request.form()
    upload = form.get("file") or form.get("resume")
    if not upload or not hasattr(upload, "read"):
        raise HTTPException(status_code=400, detail="Upload a resume file to scan")
    content = await upload.read()
    filename = getattr(upload, "filename", "resume.pdf") or "resume.pdf"
    if not content:
        raise HTTPException(status_code=400, detail="Resume content is required")
    text = extract_resume_text(content, filename)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in resume")
    extraction = ai_service.extract_resume_profile(text, pdf_content=content if Path(filename).suffix.lower() == ".pdf" else None, filename=filename)
    with closing(connect()) as db:
        next_number = db.execute("SELECT COALESCE(MAX(CAST(SUBSTR(candidate_id, 4) AS INTEGER)), 0) + 1 FROM candidates").fetchone()[0]
        candidate_id = f"CAN{int(next_number):03d}"
        derived = derive_candidate_from_resume(extraction, candidate_id)
        candidate_email = derived["email"]
        try:
            db.execute(
                "INSERT INTO candidates (candidate_id, candidate_code, first_name, last_name, email, location, total_experience_years, highest_education, education_field, current_role, application_date, source, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    candidate_id,
                    f"C{int(next_number):03d}",
                    derived["first_name"],
                    derived["last_name"],
                    candidate_email,
                    derived["location"],
                    derived["total_experience_years"],
                    derived["highest_education"],
                    derived["education_field"],
                    derived["current_role"],
                    datetime.now(timezone.utc).date().isoformat(),
                    "resume_scan",
                    "applied",
                ),
            )
            db.execute(
                "INSERT INTO candidate_evidence (evidence_id, candidate_id, evidence_type, source_document, source_text, evidence_strength, confidence_score, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (f"RESUME_{candidate_id}_{int(datetime.now().timestamp())}", candidate_id, "resume", filename, text, "documented", 1.0, datetime.now(timezone.utc).isoformat()),
            )
            persist_resume_profile(db, candidate_id, filename, extraction)
            sync_applicant_record(db, candidate_id)
            db.commit()
        except sqlite3.IntegrityError as error:
            raise HTTPException(status_code=409, detail="A candidate with this email already exists") from error
        result = candidate_detail(db, candidate_id)
        result["resume_extraction"] = extraction
        return result


@app.get("/api/candidates/{candidate_id}")
def candidate_data(candidate_id: str) -> dict[str, Any]:
    with closing(connect()) as db:
        return candidate_detail(db, candidate_id)


@app.post("/api/candidates/{candidate_id}/analyze")
def analyze_candidate(candidate_id: str) -> dict[str, Any]:
    with closing(connect()) as db:
        evidence = db.execute("SELECT source_text FROM candidate_evidence WHERE candidate_id = ? AND evidence_type = 'resume' ORDER BY created_at DESC LIMIT 1", (candidate_id,)).fetchone()
        extraction = ai_service.extract_resume_profile(evidence["source_text"] if evidence else "")
        if evidence and evidence["source_text"]:
            text = evidence["source_text"].lower()
            catalog = db.execute("SELECT skill_id, training_name FROM skill_training_catalog").fetchall()
            for skill in catalog:
                skill_name = skill["training_name"].split()[0].lower()
                if len(skill_name) > 2 and skill_name in text:
                    skill_exists = db.execute("SELECT 1 FROM candidate_skills WHERE candidate_id = ? AND skill_id = ?", (candidate_id, skill["skill_id"])).fetchone()
                    if not skill_exists:
                        db.execute("INSERT INTO candidate_skills (candidate_skill_id, candidate_id, skill_id, proficiency_level, proficiency_score, years_experience, evidence_text, evidence_source, confidence_score, verification_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (f"EXTRACT_{candidate_id}_{skill['skill_id']}", candidate_id, skill["skill_id"], "not_stated", 0, 0, f"Found exact skill text in uploaded resume: {skill['training_name']}", "resume", 1.0, "unverified"))
            db.commit()
        result = candidate_detail(db, candidate_id)
        result["resume_extraction"] = extraction
        return result


@app.post("/api/candidates/{candidate_id}/match/{job_id}")
def match_candidate(candidate_id: str, job_id: str) -> dict[str, Any]:
    with closing(connect()) as db:
        return calculate_candidate_match(db, candidate_id, job_id)


@app.get("/api/jobs/{job_id}/candidates")
def job_candidates(job_id: str) -> list[dict[str, Any]]:
    with closing(connect()) as db:
        rows = db.execute("SELECT s.*, TRIM(c.first_name || ' ' || c.last_name) AS name, c.current_role, c.status FROM candidate_job_scores s INNER JOIN candidates c ON c.candidate_id = s.candidate_id WHERE s.job_id = ? ORDER BY s.overall_match_score DESC", (job_id,)).fetchall()
    return [dict(row) for row in rows]


@app.get("/api/jobs/{job_id}/candidates/{candidate_id}/score")
def candidate_job_score(job_id: str, candidate_id: str) -> dict[str, Any]:
    with closing(connect()) as db:
        return calculate_candidate_match(db, candidate_id, job_id)


@app.patch("/api/candidates/{candidate_id}/status")
def candidate_status(candidate_id: str, request: CandidateStatusUpdate, token: str | None = None) -> dict[str, Any]:
    require_session(token)
    allowed = {"applied", "screening", "shortlisted", "interview", "hired", "rejected"}
    if request.status.lower() not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported candidate status")
    with closing(connect()) as db:
        cursor = db.execute("UPDATE candidates SET status = ? WHERE candidate_id = ?", (request.status.lower(), candidate_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")
        db.commit()
        return candidate_detail(db, candidate_id)


@app.post("/api/candidates/{candidate_id}/resume")
async def candidate_resume(candidate_id: str, request: Request, token: str | None = None) -> dict[str, Any]:
    require_session(token)
    filename = request.headers.get("x-filename", "resume.txt")
    if request.headers.get("content-type", "").startswith("multipart/form-data"):
        form = await request.form()
        upload = form.get("file") or form.get("resume")
        if not upload or not hasattr(upload, "read"):
            raise HTTPException(status_code=400, detail="Upload a resume in the file field")
        content = await upload.read()
        filename = getattr(upload, "filename", filename) or filename
    else:
        content = await request.body()
    if not content:
        raise HTTPException(status_code=400, detail="Resume content is required")
    text = extract_resume_text(content, filename)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in resume")
    extraction = ai_service.extract_resume_profile(text, pdf_content=content if Path(filename).suffix.lower() == ".pdf" else None, filename=filename)
    with closing(connect()) as db:
        if not db.execute("SELECT 1 FROM candidates WHERE candidate_id = ?", (candidate_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Candidate not found")
        db.execute("UPDATE candidates SET resume_file = ? WHERE candidate_id = ?", (filename, candidate_id))
        db.execute("INSERT INTO candidate_evidence (evidence_id, candidate_id, evidence_type, source_document, source_text, evidence_strength, confidence_score, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (f"RESUME_{candidate_id}_{int(datetime.now().timestamp())}", candidate_id, "resume", filename, text, "documented", 1.0, datetime.now(timezone.utc).isoformat()))
        persist_resume_profile(db, candidate_id, filename, extraction)
        db.commit()
        result = candidate_detail(db, candidate_id)
        result["resume_extraction"] = extraction
        return result


@app.post("/api/interviews")
def create_interview(interview: InterviewCreate, token: str | None = None) -> dict[str, Any]:
    require_session(token)
    interview_id = f"INT_{interview.candidate_id}_{interview.job_id}_{interview.interview_round}"
    with closing(connect()) as db:
        db.execute("INSERT OR REPLACE INTO interviews (interview_id, candidate_id, job_id, interview_round, interview_date, status) VALUES (?, ?, ?, ?, ?, ?)", (interview_id, interview.candidate_id, interview.job_id, interview.interview_round, interview.interview_date, "scheduled"))
        requirements = db.execute("SELECT skill_id, required_proficiency, skill_id AS skill_name FROM job_requirements WHERE job_id = ? ORDER BY is_mandatory DESC, weight DESC LIMIT 8", (interview.job_id,)).fetchall()
        for index, requirement in enumerate(requirements, 1):
            question_id = f"Q_{interview_id}_{index}"
            db.execute("INSERT OR REPLACE INTO interview_questions (question_id, interview_id, skill_id, question, difficulty, question_type) VALUES (?, ?, ?, ?, ?, ?)", (question_id, interview_id, requirement["skill_id"], f"Explain your practical experience with {requirement['skill_name']} and describe one result you delivered.", requirement["required_proficiency"] or "intermediate", "technical"))
        db.commit()
        return {"interview_id": interview_id, "questions": [dict(row) for row in db.execute("SELECT * FROM interview_questions WHERE interview_id = ?", (interview_id,)).fetchall()]}


@app.post("/api/interviews/{interview_id}/evaluate")
def evaluate_interview(interview_id: str, answer: InterviewAnswerCreate, token: str | None = None) -> dict[str, Any]:
    require_session(token)
    with closing(connect()) as db:
        question = db.execute("SELECT * FROM interview_questions WHERE question_id = ? AND interview_id = ?", (answer.question_id, interview_id)).fetchone()
        interview = db.execute("SELECT candidate_id FROM interviews WHERE interview_id = ?", (interview_id,)).fetchone()
        if not question or not interview:
            raise HTTPException(status_code=404, detail="Interview question not found")
        length_score = min(100, 45 + len(answer.answer_text.split()) * 2)
        answer_id = f"ANS_{interview_id}_{answer.question_id}"
        evidence = "Evaluation is based on documented answer length and stored response; HR review is required for final judgment."
        db.execute("INSERT OR REPLACE INTO interview_answers (answer_id, question_id, candidate_id, answer_text, technical_correctness, conceptual_understanding, problem_solving, practical_reasoning, communication, evidence, ai_confidence) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (answer_id, answer.question_id, interview["candidate_id"], answer.answer_text, length_score, length_score, length_score, length_score, min(100, length_score + 5), evidence, 0.35))
        db.commit()
        return {"answer_id": answer_id, "technical_correctness": length_score, "conceptual_understanding": length_score, "problem_solving": length_score, "practical_reasoning": length_score, "communication": min(100, length_score + 5), "evidence": [evidence], "ai_confidence": 0.35}


@app.post("/api/jobs")
def create_job(job: RoleCreate, token: str | None = None) -> dict[str, Any]:
    actor = require_session(token)
    with closing(connect()) as db:
        cursor = db.execute("INSERT INTO jobs (title, department, applicants, status) VALUES (?, ?, 0, ?)", (job.title, job.department, job.status))
        notify_activity(db, actor, "role_created", "New role created", f"{actor['name']} created the {job.title} role for {job.department}.")
        db.commit()
        row = db.execute("SELECT * FROM jobs WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@app.get("/api/applicants")
def applicants() -> list[dict[str, Any]]:
    with closing(connect()) as db:
        rows = db.execute("SELECT id, printf('CAN%03d', id) AS candidate_id, name, role, experience, skills, stage, match_score AS match FROM applicants ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]


@app.post("/api/applicants")
def create_applicant(applicant: ApplicantCreate, token: str | None = None) -> dict[str, Any]:
    actor = require_session(token)
    with closing(connect()) as db:
        duplicate = db.execute("SELECT id FROM applicants WHERE lower(trim(name)) = lower(trim(?)) AND lower(trim(role)) = lower(trim(?))", (applicant.name, applicant.role)).fetchone()
        if duplicate:
            raise HTTPException(status_code=409, detail="This applicant is already registered for that role")
        cursor = db.execute("INSERT INTO applicants (name, role, experience, skills, stage, match_score) VALUES (?, ?, ?, ?, ?, ?)", (applicant.name, applicant.role, applicant.experience, applicant.skills, applicant.stage, 70))
        db.execute("UPDATE jobs SET applicants = applicants + 1 WHERE title = ?", (applicant.role,))
        notify_activity(db, actor, "applicant_created", "New applicant added", f"{actor['name']} added {applicant.name} for the {applicant.role} role.", notify_hr=True)
        db.commit()
        row = db.execute("SELECT id, name, role, experience, skills, stage, match_score AS match FROM applicants WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@app.post("/api/applicants/{applicant_id}/hire")
def hire_applicant(applicant_id: int, token: str | None = None) -> dict[str, Any]:
    actor = require_session(token)
    with closing(connect()) as db:
        applicant = db.execute("SELECT * FROM applicants WHERE id = ?", (applicant_id,)).fetchone()
        if not applicant:
            raise HTTPException(status_code=404, detail="Applicant not found")
        department_row = db.execute("SELECT department FROM jobs WHERE title = ? ORDER BY id LIMIT 1", (applicant["role"],)).fetchone()
        department = department_row["department"] if department_row else "People"
        employee_cursor = db.execute("INSERT INTO employees (name, role, department, location, tenure_years, performance_score, satisfaction_score, overtime, skills, status) VALUES (?, ?, ?, ?, 0, 3.5, 3.5, 0, ?, 'Active')", (applicant["name"], applicant["role"], department, "Unassigned", applicant["skills"]))
        db.execute("UPDATE applicants SET stage = 'Hired' WHERE id = ?", (applicant_id,))
        db.execute("UPDATE jobs SET applicants = CASE WHEN applicants > 0 THEN applicants - 1 ELSE 0 END WHERE title = ?", (applicant["role"],))
        notify_activity(db, actor, "applicant_hired", "Applicant hired", f"{actor['name']} hired {applicant['name']} as {applicant['role']}.", notify_hr=True)
        db.commit()
        employee = db.execute("SELECT * FROM employees WHERE id = ?", (employee_cursor.lastrowid,)).fetchone()
    return {"applicant": dict(applicant), "employee": dict(employee)}


@app.post("/api/applicants/{applicant_id}/reject")
def reject_applicant(applicant_id: int, token: str | None = None) -> dict[str, Any]:
    actor = require_session(token)
    with closing(connect()) as db:
        applicant = db.execute("SELECT * FROM applicants WHERE id = ?", (applicant_id,)).fetchone()
        if not applicant:
            raise HTTPException(status_code=404, detail="Applicant not found")
        db.execute("DELETE FROM applicants WHERE id = ?", (applicant_id,))
        db.execute("UPDATE jobs SET applicants = CASE WHEN applicants > 0 THEN applicants - 1 ELSE 0 END WHERE title = ?", (applicant["role"],))
        notify_activity(db, actor, "applicant_rejected", "Applicant rejected", f"{actor['name']} rejected {applicant['name']} for {applicant['role']}.", notify_hr=True)
        db.commit()
    return {"ok": True, "applicant_id": applicant_id}


@app.get("/api/insights")
def insights() -> dict[str, Any]:
    with closing(connect()) as db:
        employees = db.execute("SELECT * FROM employees WHERE status = 'Active' ORDER BY name").fetchall()
        plans = db.execute("SELECT learning_plans.id, learning_plans.employee_id, employees.name AS employee_name, learning_plans.skill, learning_plans.title, learning_plans.status, learning_plans.created_at FROM learning_plans INNER JOIN employees ON employees.id = learning_plans.employee_id WHERE employees.status = 'Active' ORDER BY learning_plans.id DESC").fetchall()
    risk_rows = []
    for employee in employees:
        analysis = analyze_employee(employee)
        risk_rows.append({"employee_id": employee["id"], "name": employee["name"], "role": employee["role"], "department": employee["department"], "risk_score": analysis["retention_risk"], "engagement_score": analysis["engagement_score"], "growth_readiness": analysis["growth_readiness"], "workload_index": analysis["workload_index"], "factors": analysis["factors"]})
    department_rows: dict[str, list[sqlite3.Row]] = {}
    for employee in employees:
        department_rows.setdefault(employee["department"], []).append(employee)
    departments = []
    for department, members in department_rows.items():
        member_analyses = [analyze_employee(member) for member in members]
        departments.append({
            "name": department,
            "headcount": len(members),
            "satisfaction": round(sum(member["satisfaction_score"] for member in members) / len(members), 2),
            "performance": round(sum(member["performance_score"] for member in members) / len(members), 2),
            "engagement": round(sum(item["engagement_score"] for item in member_analyses) / len(member_analyses)),
            "risk": round(sum(item["retention_risk"] for item in member_analyses) / len(member_analyses), 2),
        })
    return {
        "risks": sorted(risk_rows, key=lambda item: item["risk_score"], reverse=True),
        "skill_gaps": build_skill_gaps(employees),
        "departments": sorted(departments, key=lambda item: item["risk"], reverse=True),
        "learning_plans": [dict(plan) for plan in plans],
    }


@app.get("/api/kpi-config")
def kpi_config(token: str | None = None) -> list[dict[str, Any]]:
    with closing(connect()) as db:
        rows = db.execute(
            """
            SELECT r.role_id, r.role_name, rk.role_kpi_id, k.kpi_name,
                   rk.weight, rk.target_value, rk.minimum_value,
                   rk.maximum_value, rk.measurement_type, rk.direction,
                   rk.is_mandatory, rk.active
            FROM roles r
            INNER JOIN role_kpis rk ON rk.role_id = r.role_id
            INNER JOIN kpis k ON k.kpi_id = rk.kpi_id
            WHERE rk.active = 1
            ORDER BY r.role_name, rk.weight DESC, k.kpi_name
            """
        ).fetchall()
    return [dict(row) for row in rows]


@app.put("/api/kpi-config/{role_id}")
def update_kpi_config(role_id: str, request: RoleKPIConfigUpdate, token: str | None = None) -> list[dict[str, Any]]:
    require_session(token, admin=True)
    total_weight = sum(item.weight for item in request.items)
    if abs(total_weight - 1.0) > 0.001:
        raise HTTPException(status_code=400, detail="Active KPI weights for a role must total 100%.")
    with closing(connect()) as db:
        expected = {row["role_kpi_id"] for row in db.execute("SELECT role_kpi_id FROM role_kpis WHERE role_id = ? AND active = 1", (role_id,)).fetchall()}
        submitted = {item.role_kpi_id for item in request.items}
        if expected != submitted:
            raise HTTPException(status_code=400, detail="Submit every active KPI for this role exactly once.")
        for item in request.items:
            db.execute("UPDATE role_kpis SET weight = ? WHERE role_id = ? AND role_kpi_id = ?", (item.weight, role_id, item.role_kpi_id))
        db.commit()
        rows = db.execute("SELECT role_kpi_id, weight FROM role_kpis WHERE role_id = ? AND active = 1 ORDER BY weight DESC", (role_id,)).fetchall()
    return [dict(row) for row in rows]


@app.get("/api/learning-plans")
def learning_plans(token: str | None = None) -> list[dict[str, Any]]:
    require_session(token)
    with closing(connect()) as db:
        rows = db.execute("SELECT learning_plans.id, learning_plans.employee_id, employees.name AS employee_name, learning_plans.skill, learning_plans.title, learning_plans.status, learning_plans.created_at FROM learning_plans INNER JOIN employees ON employees.id = learning_plans.employee_id ORDER BY learning_plans.id DESC").fetchall()
    return [dict(row) for row in rows]


@app.post("/api/learning-plans")
def create_learning_plan(plan: LearningPlanCreate, token: str | None = None) -> dict[str, Any]:
    actor = require_session(token)
    with closing(connect()) as db:
        employee = db.execute("SELECT id FROM employees WHERE id = ?", (plan.employee_id,)).fetchone()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        cursor = db.execute("INSERT INTO learning_plans (employee_id, skill, title, created_at) VALUES (?, ?, ?, ?)", (plan.employee_id, plan.skill, plan.title, datetime.now(timezone.utc).isoformat()))
        notify_activity(db, actor, "learning_plan_created", "Learning plan created", f"{actor['name']} created a learning plan for {plan.skill}.")
        db.commit()
        row = db.execute("SELECT learning_plans.id, learning_plans.employee_id, employees.name AS employee_name, learning_plans.skill, learning_plans.title, learning_plans.status, learning_plans.created_at FROM learning_plans INNER JOIN employees ON employees.id = learning_plans.employee_id WHERE learning_plans.id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@app.get("/api/policies")
def policies() -> list[dict[str, Any]]:
    with closing(connect()) as db:
        rows = db.execute("SELECT id, title, section, content FROM policies ORDER BY id").fetchall()
    return [dict(row) for row in rows]


@app.post("/api/policies/ask")
async def ask_policy(question: PolicyQuestion) -> dict[str, Any]:
    with closing(connect()) as db:
        context = [dict(row) for row in db.execute("SELECT title, section, content FROM policies").fetchall()]
    return await ai_service.answer_policy_question(question.question, context)


@app.post("/api/chat")
async def chat(request: ChatRequest, token: str | None = None) -> dict[str, Any]:
    user = require_session(token)
    with closing(connect()) as db:
        employee_count = db.execute("SELECT COUNT(*) FROM employees WHERE status = 'Active'").fetchone()[0]
        open_roles = db.execute("SELECT COUNT(*) FROM jobs WHERE status != 'Closed'").fetchone()[0]
        applicant_count = db.execute("SELECT COUNT(*) FROM applicants WHERE stage NOT IN ('Hired', 'Rejected')").fetchone()[0]
        policy_titles = [row["title"] for row in db.execute("SELECT title FROM policies ORDER BY id").fetchall()]
    context = f"Signed-in role: {user['role']}. Active employees: {employee_count}. Open roles: {open_roles}. Active applicants: {applicant_count}. Available policy sources: {', '.join(policy_titles)}."
    return await ai_service.answer_hr_chat(request.message, context)


@app.post("/api/policies")
def create_policy(policy: PolicyCreate, token: str | None = None) -> dict[str, Any]:
    actor = require_session(token)
    with closing(connect()) as db:
        cursor = db.execute("INSERT INTO policies (title, section, content) VALUES (?, ?, ?)", (policy.title, policy.section, policy.content))
        notify_activity(db, actor, "policy_created", "New policy added", f"{actor['name']} added the {policy.title} policy source.")
        db.commit()
        row = db.execute("SELECT id, title, section, content FROM policies WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


if FRONTEND_PATH.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_PATH, html=True), name="frontend")
