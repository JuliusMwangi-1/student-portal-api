from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json
import hashlib
from typing import List

app = FastAPI()
security = HTTPBasic()

STUDENTS_FILE = "students.json"

class Student:
    def __init__(self, username: str, password: str, grades: List[int]):
        self.username = username
        self.password = self.hash_password(password)
        self.grades = grades

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        return self.password == hashlib.sha256(password.encode()).hexdigest()

def load_students():
    try:
        with open(STUDENTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error reading student data")

def save_students(students):
    try:
        with open(STUDENTS_FILE, "w") as f:
            json.dump(students, f, indent=4)
    except Exception:
        raise HTTPException(status_code=500, detail="Error saving student data")

def get_current_student(credentials: HTTPBasicCredentials = Depends(security)):
    students = load_students()
    username = credentials.username
    password = credentials.password

    if username not in students:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    stored_password = students[username]["password"]
    hashed_input = hashlib.sha256(password.encode()).hexdigest()

    if hashed_input != stored_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return students[username]

@app.post("/register/")
def register(username: str, password: str, grades: List[int]):
    students = load_students()

    if username in students:
        raise HTTPException(status_code=400, detail="Username already exists")

    student = Student(username, password, grades)
    students[username] = {"password": student.password, "grades": student.grades}
    save_students(students)

    return {"message": "Student registered successfully"}

@app.post("/login/")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    student = get_current_student(credentials)
    return {"message": f"Welcome {credentials.username}"}

@app.get("/grades/")
def get_grades(student: dict = Depends(get_current_student)):
    return {"grades": student["grades"]}
