# main.py
# FastAPI application entry point — registers routes and starts the app

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

import models
import schemas
from database import engine, get_db

# ---------------------------------------------------------------------------
# Database initialisation
# ---------------------------------------------------------------------------
# Create all tables declared in models.py (safe to call on every startup)
models.Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Student Management System API",
    description=(
        "A production-ready REST API to manage students using "
        "FastAPI + SQLAlchemy + SQLite."
    ),
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)


# ===========================================================================
# 1. CREATE STUDENT  —  POST /create-student/
# ===========================================================================
@app.post(
    "/create-student/",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    tags=["Students"],
)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new student in the database.

    - **name**: Full name (2–100 characters)
    - **email**: Valid, unique email address
    - **age**: Positive integer
    - **course**: Enrolled course name (2–100 characters)
    """
    # Check for duplicate email before attempting the INSERT
    existing = db.query(models.Student).filter(
        models.Student.email == student.email
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A student with email '{student.email}' already exists.",
        )

    # Map the Pydantic schema to the ORM model
    new_student = models.Student(**student.model_dump())

    try:
        db.add(new_student)
        db.commit()
        db.refresh(new_student)  # Reload from DB to get the generated id
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error — email may already be taken.",
        )

    return new_student


# ===========================================================================
# 2. GET ALL STUDENTS  —  GET /students-all/
# ===========================================================================
@app.get(
    "/students-all/",
    response_model=List[schemas.StudentResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve all students",
    tags=["Students"],
)
def get_all_students(db: Session = Depends(get_db)):
    """
    Return a list of every student in the database.
    """
    students = db.query(models.Student).all()
    return students


# ===========================================================================
# 3. GET SINGLE STUDENT  —  GET /student/{id}
# ===========================================================================
@app.get(
    "/student/{id}",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a student by ID",
    tags=["Students"],
)
def get_student(id: int, db: Session = Depends(get_db)):
    """
    Fetch a single student record by their numeric **id**.

    Raises **404 Not Found** if the id does not exist.
    """
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id={id} not found.",
        )
    return student


# ===========================================================================
# 4. UPDATE STUDENT  —  PUT /update-students/{id}
# ===========================================================================
@app.put(
    "/update-students/{id}",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a student by ID",
    tags=["Students"],
)
def update_student(
    id: int,
    updated_data: schemas.StudentUpdate,
    db: Session = Depends(get_db),
):
    """
    Partially or fully update an existing student record.

    Only the fields provided in the request body are modified.
    Raises **404** if the student does not exist.
    Raises **400** if the new email is already used by another student.
    """
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id={id} not found.",
        )

    # If the caller wants to change the email, check uniqueness first
    if updated_data.email and updated_data.email != student.email:
        email_conflict = db.query(models.Student).filter(
            models.Student.email == updated_data.email
        ).first()
        if email_conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{updated_data.email}' is already in use by another student.",
            )

    # Apply only the fields that were explicitly provided (exclude_unset=True)
    update_fields = updated_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(student, field, value)

    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update failed due to a database integrity error.",
        )

    return student


# ===========================================================================
# 5. DELETE STUDENT  —  DELETE /delete-students/{id}
# ===========================================================================
@app.delete(
    "/delete-students/{id}",
    response_model=schemas.MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a student by ID",
    tags=["Students"],
)
def delete_student(id: int, db: Session = Depends(get_db)):
    """
    Permanently remove a student record from the database.

    Raises **404** if the student does not exist.
    """
    student = db.query(models.Student).filter(models.Student.id == id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id={id} not found.",
        )

    db.delete(student)
    db.commit()

    return {"message": f"Student with id={id} has been deleted successfully."}


# ===========================================================================
# Health-check endpoint (bonus — useful for deployment monitoring)
# ===========================================================================
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Student Management System API is running."}
