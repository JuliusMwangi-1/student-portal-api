from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import hashlib
import json
import os

app = FastAPI()
security = HTTPBasic()

STUDENTS_FILE = "students.json"

# Helper functions
def load_students():
    if not os.path.exists(STUDENTS_FILE):
        return []
    try:
        with open(STUDENTS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_students(students):
    try:
        with open(STUDENTS_FILE, "w") as f:
            json.dump(students, f, indent=4)
    except Exception:
        raise HTTPException(status_code=500, detail="Error saving student data")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Endpoints
@app.post("/register/")
def register(username: str, password: str):
    students = load_students()

    if any(student["username"] == username for student in students):
        raise HTTPException(status_code=400, detail="Username already exists")

    new_student = {
        "username": username,
        "password": hash_password(password),
        "grades": []
    }
    students.append(new_student)
    save_students(students)
    return {"message": "Student registered successfully"}

@app.post("/login/")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    students = load_students()
    hashed = hash_password(credentials.password)

    for student in students:
        if student["username"] == credentials.username and student["password"] == hashed:
            return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/grades/")
def get_grades(credentials: HTTPBasicCredentials = Depends(security)):
    students = load_students()
    hashed = hash_password(credentials.password)

    for student in students:
        if student["username"] == credentials.username and student["password"] == hashed:
            return {"grades": student["grades"]}
    raise HTTPException(status_code=401, detail="Unauthorized")
