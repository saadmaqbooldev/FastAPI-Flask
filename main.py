from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(
    title="Student Management API",
    description="CRUD API using Python List",
    version="1.0"
)

students = []


class Student(BaseModel):
    id: int
    name: str
    age: int
    course: str


# Home API
@app.get("/")
def home():
    return {"message": "Welcome to Student Management API"}


# Create Student
@app.post("/students")
def add_student(student: Student):
    for s in students:
        if s["id"] == student.id:
            raise HTTPException(status_code=400, detail="Student ID already exists")

    students.append(student.model_dump())

    return {
        "message": "Student Added Successfully",
        "student": student
    }


# Get All Students
@app.get("/students")
def get_students():
    return students


# Get Student By ID
@app.get("/students/{student_id}")
def get_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student

    raise HTTPException(status_code=404, detail="Student Not Found")


# Update Student
@app.put("/students/{student_id}")
def update_student(student_id: int, updated_student: Student):

    for index, student in enumerate(students):

        if student["id"] == student_id:

            students[index] = updated_student.model_dump()

            return {
                "message": "Student Updated Successfully",
                "student": updated_student
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


# Search Student By Course
@app.get("/search")
def search_student(course: str = Query(..., description="Course Name")):

    result = []

    for student in students:
        if student["course"].lower() == course.lower():
            result.append(student)

    return result