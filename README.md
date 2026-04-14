# Student Management System — REST API

A production-quality REST API built with **FastAPI + SQLAlchemy + SQLite**.

---

## Project Structure

```
student_management/
├── main.py       # FastAPI app, route handlers
├── database.py   # Engine, session factory, get_db dependency
├── models.py     # SQLAlchemy ORM model (Student table)
└── schemas.py    # Pydantic request / response schemas
```

---

## Setup & Run

### 1. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy pydantic[email]
```

### 2. Start the server

```bash
uvicorn main:app --reload
```

> The `--reload` flag auto-restarts the server on code changes (development only).  
> The SQLite database file `students.db` is created automatically on first run.

### 3. Open interactive docs

| UI      | URL                                  |
|---------|--------------------------------------|
| Swagger | http://127.0.0.1:8000/docs           |
| ReDoc   | http://127.0.0.1:8000/redoc          |

---

## API Endpoints

| Method | Endpoint                  | Description             |
|--------|---------------------------|-------------------------|
| GET    | `/`                       | Health check            |
| POST   | `/create-student/`        | Create a new student    |
| GET    | `/students-all/`          | Get all students        |
| GET    | `/student/{id}`           | Get student by ID       |
| PUT    | `/update-students/{id}`   | Update student by ID    |
| DELETE | `/delete-students/{id}`   | Delete student by ID    |

---

## Example API Requests (cURL)

### Create a Student
```bash
curl -X POST http://127.0.0.1:8000/create-student/ \
  -H "Content-Type: application/json" \
  -d '{
    "name":   "Alice Johnson",
    "email":  "alice@example.com",
    "age":    21,
    "course": "Computer Science"
  }'
```

**Response (201 Created)**
```json
{
  "id":     1,
  "name":   "Alice Johnson",
  "email":  "alice@example.com",
  "age":    21,
  "course": "Computer Science"
}
```

---

### Get All Students
```bash
curl http://127.0.0.1:8000/students-all/
```

**Response (200 OK)**
```json
[
  { "id": 1, "name": "Alice Johnson", "email": "alice@example.com", "age": 21, "course": "Computer Science" },
  { "id": 2, "name": "Bob Smith",     "email": "bob@example.com",   "age": 23, "course": "Data Science"     }
]
```

---

### Get Student by ID
```bash
curl http://127.0.0.1:8000/student/1
```

**Response (200 OK)**
```json
{ "id": 1, "name": "Alice Johnson", "email": "alice@example.com", "age": 21, "course": "Computer Science" }
```

---

### Update Student (partial update supported)
```bash
curl -X PUT http://127.0.0.1:8000/update-students/1 \
  -H "Content-Type: application/json" \
  -d '{
    "age":    22,
    "course": "Data Science"
  }'
```

**Response (200 OK)**
```json
{ "id": 1, "name": "Alice Johnson", "email": "alice@example.com", "age": 22, "course": "Data Science" }
```

---

### Delete Student
```bash
curl -X DELETE http://127.0.0.1:8000/delete-students/1
```

**Response (200 OK)**
```json
{ "message": "Student with id=1 has been deleted successfully." }
```

---

## Error Responses

| Scenario              | Status | Example Detail                                      |
|-----------------------|--------|-----------------------------------------------------|
| Student not found     | 404    | `"Student with id=99 not found."`                   |
| Duplicate email       | 400    | `"A student with email 'x@y.com' already exists."`  |
| Validation failure    | 422    | Pydantic auto-generates field-level error details   |

---

## Suggested Production Improvements

### 🔐 1. Authentication & Authorization
Add JWT-based auth with `python-jose` + `passlib`:
- `POST /auth/register` — register a user
- `POST /auth/login` — return a signed JWT token
- Protect all student routes with an `OAuth2PasswordBearer` dependency
- Role-based access control: `admin` can delete/update, `viewer` can only read

### 📄 2. Pagination
Replace `db.query(...).all()` with limit/offset:
```python
@app.get("/students-all/")
def get_all_students(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Student).offset(skip).limit(limit).all()
```
Add a `total` count in the response for frontend page controls.

### 🔍 3. Filtering & Searching
Allow filtering by course, age range, or name search:
```python
def get_all_students(
    course: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Student)
    if course:  query = query.filter(models.Student.course == course)
    if min_age: query = query.filter(models.Student.age >= min_age)
    if max_age: query = query.filter(models.Student.age <= max_age)
    if search:  query = query.filter(models.Student.name.ilike(f"%{search}%"))
    return query.all()
```

### 🗃️ 4. Switch to PostgreSQL for Production
Simply change `DATABASE_URL`:
```python
DATABASE_URL = "postgresql://user:password@localhost/students_db"
```
Then install `psycopg2-binary`.

### 🧪 5. Testing
Add `pytest` + `httpx` integration tests using an in-memory SQLite test database.

### 📦 6. Alembic Migrations
Use Alembic to manage schema changes safely instead of `create_all()`.

### 🐳 7. Dockerise
Add a `Dockerfile` and `docker-compose.yml` to containerise the app alongside a PostgreSQL instance.
```
