from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from statistics import mean

app = FastAPI(
    title="Student Management API",
    description="CRUD API using Python List",
    version="1.2"
)

students = []


class Student(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., gt=0, lt=100)
    course: str = Field(..., min_length=1)


# For PATCH — every field optional so client can update just one at a time
class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    age: Optional[int] = Field(None, gt=0, lt=100)
    course: Optional[str] = Field(None, min_length=1)


# Home API
@app.get("/")
def home():
    return {"message": "Welcome to Student Management API"}


# Create Student
@app.post("/students", status_code=201)
def add_student(student: Student):
    for s in students:
        if s["id"] == student.id:
            raise HTTPException(status_code=400, detail="Student ID already exists")

    students.append(student.model_dump())

    return {
        "message": "Student Added Successfully",
        "student": student
    }


# Get All Students — with optional filtering & sorting
@app.get("/students")
def get_students(
    course: Optional[str] = Query(None, description="Filter by course"),
    min_age: Optional[int] = Query(None, description="Minimum age"),
    max_age: Optional[int] = Query(None, description="Maximum age"),
    sort_by: Optional[str] = Query(None, description="Sort by 'name' or 'age'"),
):
    result = students

    if course:
        result = [s for s in result if s["course"].lower() == course.lower()]
    if min_age is not None:
        result = [s for s in result if s["age"] >= min_age]
    if max_age is not None:
        result = [s for s in result if s["age"] <= max_age]

    if sort_by in ("name", "age"):
        result = sorted(result, key=lambda s: s[sort_by])

    return {"count": len(result), "students": result}


# Get Student By ID
@app.get("/students/{student_id}")
def get_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student

    raise HTTPException(status_code=404, detail="Student Not Found")


# Update Student (Full Update — replaces all fields)
@app.put("/students/{student_id}")
def update_student(student_id: int, updated_student: Student):

    # Block path/body ID mismatch (e.g. PUT /students/5 with body id=999)
    if updated_student.id != student_id:
        raise HTTPException(
            status_code=400,
            detail=f"ID in URL ({student_id}) does not match ID in request body ({updated_student.id})"
        )

    for index, student in enumerate(students):

        if student["id"] == student_id:

            students[index] = updated_student.model_dump()

            return {
                "message": "Student Updated Successfully",
                "student": updated_student
            }

    raise HTTPException(status_code=404, detail="Student Not Found")


# Partial Update Student (only send the fields you want to change)
@app.patch("/students/{student_id}")
def partial_update_student(student_id: int, updates: StudentUpdate):

    for student in students:
        if student["id"] == student_id:

            update_data = updates.model_dump(exclude_unset=True)
            student.update(update_data)

            return {
                "message": "Student Updated Successfully",
                "student": student
            }

    raise HTTPException(status_code=404, detail="Student Not Found")


# Delete Student
@app.delete("/students/{student_id}")
def delete_student(student_id: int):

    for student in students:

        if student["id"] == student_id:
            students.remove(student)

            return {"message": "Student Deleted Successfully"}

    raise HTTPException(status_code=404, detail="Student Not Found")


# Delete All Students
@app.delete("/students")
def delete_all_students():
    count = len(students)
    students.clear()
    return {"message": f"Deleted {count} students"}


# Search Student By Course or Name (partial match, plus optional age range)
@app.get("/search")
def search_student(
    course: Optional[str] = Query(None, description="Course Name"),
    name: Optional[str] = Query(None, description="Student Name (partial match)"),
    min_age: Optional[int] = Query(None),
    max_age: Optional[int] = Query(None),
):
    result = students

    if course:
        result = [s for s in result if s["course"].lower() == course.lower()]
    if name:
        result = [s for s in result if name.lower() in s["name"].lower()]
    if min_age is not None:
        result = [s for s in result if s["age"] >= min_age]
    if max_age is not None:
        result = [s for s in result if s["age"] <= max_age]

    return result


# Stats — total students, avg age, count per course
@app.get("/stats")
def get_stats():
    if not students:
        return {"total_students": 0, "average_age": 0, "students_per_course": {}}

    course_counts = {}
    for s in students:
        course_counts[s["course"]] = course_counts.get(s["course"], 0) + 1

    return {
        "total_students": len(students),
        "average_age": round(mean(s["age"] for s in students), 1),
        "students_per_course": course_counts,
    }