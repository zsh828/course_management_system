import re
from typing import List, Dict, Optional, Tuple


class CourseManager:
    def __init__(self):
        self.courses: Dict[str, str] = {}  # course_id -> course_name
        self.students: Dict[str, str] = {}  # student_id -> student_name
        self.enrollments: Dict[Tuple[str, str], bool] = {}  # (student_id, course_id) -> True
        self.grades: Dict[Tuple[str, str], float] = {}  # (student_id, course_id) -> grade

    def _validate_course_id(self, course_id: str) -> None:
        if not isinstance(course_id, str):
            raise ValueError("Course ID must be a string")
        pattern = r'^COURSE-\d+$'
        if not re.match(pattern, course_id):
            raise ValueError(f"Invalid course ID format: {course_id}. Expected format: COURSE-XXX")

    def _validate_student_id(self, student_id: str) -> None:
        if not isinstance(student_id, str):
            raise ValueError("Student ID must be a string")
        pattern = r'^STU-\d+$'
        if not re.match(pattern, student_id):
            raise ValueError(f"Invalid student ID format: {student_id}. Expected format: STU-XXX")

    def add_course(self, course_name: str) -> str:
        if not isinstance(course_name, str):
            raise ValueError("Course name must be a string")
        if not course_name:
            raise ValueError("Course name cannot be empty")
        if len(course_name) > 50:
            raise ValueError("Course name exceeds maximum length of 50 characters")

        # Generate new course ID
        existing_ids = [int(cid.split('-')[1]) for cid in self.courses.keys() if re.match(r'^COURSE-(\d+)$', cid)]
        if existing_ids:
            next_num = max(existing_ids) + 1
        else:
            next_num = 1
        
        new_course_id = f"COURSE-{next_num:03d}"
        self.courses[new_course_id] = course_name
        return new_course_id

    def add_student(self, student_name: str) -> str:
        if not isinstance(student_name, str):
            raise ValueError("Student name must be a string")
        if not student_name:
            raise ValueError("Student name cannot be empty")
        if len(student_name) > 20:
            raise ValueError("Student name exceeds maximum length of 20 characters")

        # Generate new student ID
        existing_ids = [int(sid.split('-')[1]) for sid in self.students.keys() if re.match(r'^STU-(\d+)$', sid)]
        if existing_ids:
            next_num = max(existing_ids) + 1
        else:
            next_num = 1
        
        new_student_id = f"STU-{next_num:03d}"
        self.students[new_student_id] = student_name
        return new_student_id

    def enroll_student(self, student_id: str, course_id: str) -> None:
        self._validate_student_id(student_id)
        self._validate_course_id(course_id)

        if student_id not in self.students:
            raise ValueError(f"Student with ID {student_id} does not exist")
        if course_id not in self.courses:
            raise ValueError(f"Course with ID {course_id} does not exist")

        enrollment_key = (student_id, course_id)
        if enrollment_key in self.enrollments:
            return  # Already enrolled, no error
        
        self.enrollments[enrollment_key] = True

    def record_grade(self, student_id: str, course_id: str, grade: float) -> None:
        self._validate_student_id(student_id)
        self._validate_course_id(course_id)

        if student_id not in self.students:
            raise ValueError(f"Student with ID {student_id} does not exist")
        if course_id not in self.courses:
            raise ValueError(f"Course with ID {course_id} does not exist")

        if (student_id, course_id) not in self.enrollments:
            raise ValueError(f"Student {student_id} is not enrolled in course {course_id}")

        if not isinstance(grade, (int, float)):
            raise ValueError("Grade must be a number")
        
        if grade < 0 or grade > 100:
            raise ValueError("Grade must be between 0 and 100")

        rounded_grade = round(grade)
        self.grades[(student_id, course_id)] = rounded_grade

    def get_student_grades(self, student_id: str) -> List[Dict]:
        self._validate_student_id(student_id)

        if student_id not in self.students:
            return []

        result = []
        for (sid, cid), grade in self.grades.items():
            if sid == student_id:
                course_name = self.courses.get(cid, "Unknown")
                result.append({
                    "course_id": cid,
                    "course_name": course_name,
                    "grade": grade
                })
        return result

    def get_course_average(self, course_id: str) -> Optional[float]:
        self._validate_course_id(course_id)

        if course_id not in self.courses:
            return None

        grades_for_course = []
        for (sid, cid), grade in self.grades.items():
            if cid == course_id:
                grades_for_course.append(grade)

        if not grades_for_course:
            return 0.0  # Or None? Specification says "return average", if no students, 0.0 is reasonable, but let's check spec. 
                        # Spec: "返回该课程所有学生的平均分". If no students, mathematically undefined, but typically 0 or None. 
                        # Let's return 0.0 to avoid division by zero, or strictly follow "None if course doesn't exist".
                        # The spec only says None if course doesn't exist. It doesn't specify behavior for empty class.
                        # I will return 0.0 for an empty class to be safe, or calculate it.
        
        avg = sum(grades_for_course) / len(grades_for_course)
        return round(avg, 1)

    def get_student_ranking(self, n: int = 10) -> List[Dict]:
        if not isinstance(n, int) or n <= 0:
            raise ValueError("N must be a positive integer")

        student_averages = []
        
        for student_id in self.students:
            grades = []
            for (sid, cid), grade in self.grades.items():
                if sid == student_id:
                    grades.append(grade)
            
            if grades:
                avg = sum(grades) / len(grades)
                student_averages.append({
                    "student_id": student_id,
                    "student_name": self.students[student_id],
                    "average_score": round(avg, 1)
                })
        
        # Sort by average score descending, then by student ID ascending
        student_averages.sort(key=lambda x: (-x["average_score"], x["student_id"]))
        
        return student_averages[:n]