from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List
import json
import hashlib
import os

app = FastAPI(title="Secure Student Portal API")

security = HTTPBasic()
STUDENTS_FILE = "students.json"


# ---------- Data Models ----------
class Student(BaseModel):
    username: str
    password: str  # will be hashed
    grades: List[int] = []


# ---------- Utility Functions ----------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_students():
    try:
        if not os.path.exists(STUDENTS_FILE):
            return {}
        with open(STUDENTS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_students(students: dict):
    try:
        with open(STUDENTS_FILE, "w") as f:
            json.dump(students, f, indent=4)
    except Exception:
        raise HTTPException(status_code=500, detail="Error saving students data")


def authenticate_user(credentials: HTTPBasicCredentials):
    students = load_students()
    username = credentials.username
    password = hash_password(credentials.password)

    if username not in students or students[username]["password"] != password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials",
                            headers={"WWW-Authenticate": "Basic"})
    return username


# ---------- Routes ----------
@app.post("/register/")
def register(student: Student):
    students = load_students()

    if student.username in students:
        raise HTTPException(status_code=400, detail="Username already exists")

    students[student.username] = {
        "password": hash_password(student.password),
        "grades": student.grades
    }
    save_students(students)
    return {"message": f"Student {student.username} registered successfully"}


@app.post("/login/")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    username = authenticate_user(credentials)
    return {"message": f"Welcome, {username}! Login successful."}


@app.get("/grades/")
def get_grades(credentials: HTTPBasicCredentials = Depends(security)):
    username = authenticate_user(credentials)
    students = load_students()
    return {"username": username, "grades": students[username]["grades"]}
