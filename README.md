# Secure Student Portal API

A FastAPI project where students can register, log in, and view their grades.

## Features
- Student registration (`/register/`)
- Secure login (`/login/`) using HTTP Basic Auth
- View grades (`/grades/`) only when authenticated
- Passwords stored as SHA256 hashes
- Data saved in `students.json`

## Run the Project
```bash
uvicorn main:app --reload
