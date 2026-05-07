from src.course_manager import CourseManager
import pytest


class TestCourseManager:
    @pytest.fixture
    def manager(self):
        return CourseManager()

    def test_add_course_success(self, manager):
        course_id = manager.add_course("Mathematics")
        assert course_id == "COURSE-001"
        assert manager.courses["COURSE-001"] == "Mathematics"

    def test_add_course_second_one(self, manager):
        manager.add_course("Mathematics")
        course_id = manager.add_course("Physics")
        assert course_id == "COURSE-002"

    def test_add_course_empty_name(self, manager):
        with pytest.raises(ValueError, match="cannot be empty"):
            manager.add_course("")

    def test_add_course_long_name(self, manager):
        long_name = "A" * 51
        with pytest.raises(ValueError, match="exceeds maximum length"):
            manager.add_course(long_name)

    def test_add_student_success(self, manager):
        student_id = manager.add_student("Alice")
        assert student_id == "STU-001"
        assert manager.students["STU-001"] == "Alice"

    def test_add_student_second_one(self, manager):
        manager.add_student("Alice")
        student_id = manager.add_student("Bob")
        assert student_id == "STU-002"

    def test_add_student_empty_name(self, manager):
        with pytest.raises(ValueError, match="cannot be empty"):
            manager.add_student("")

    def test_add_student_long_name(self, manager):
        long_name = "A" * 21
        with pytest.raises(ValueError, match="exceeds maximum length"):
            manager.add_student(long_name)

    def test_enroll_student_success(self, manager):
        cid = manager.add_course("Math")
        sid = manager.add_student("Alice")
        manager.enroll_student(sid, cid)
        assert (sid, cid) in manager.enrollments

    def test_enroll_student_not_found(self, manager):
        with pytest.raises(ValueError, match="does not exist"):
            manager.enroll_student("STU-999", "COURSE-999")

    def test_enroll_student_duplicate(self, manager):
        cid = manager.add_course("Math")
        sid = manager.add_student("Alice")
        manager.enroll_student(sid, cid)
        # Should not raise error
        manager.enroll_student(sid, cid)
        assert len([k for k in manager.enrollments.keys() if k[0] == sid and k[1] == cid]) == 1

    def test_record_grade_success(self, manager):
        cid = manager.add_course("Math")
        sid = manager.add_student("Alice")
        manager.enroll_student(sid, cid)
        manager.record_grade(sid, cid, 85.5)
        assert manager.grades[(sid, cid)] == 86  # Rounded

    def test_record_grade_not_enrolled(self, manager):
        cid = manager.add_course("Math")
        sid = manager.add_student("Alice")
        with pytest.raises(ValueError, match="not enrolled"):
            manager.record_grade(sid, cid, 85)

    def test_record_grade_out_of_range_low(self, manager):
        cid = manager.add_course("Math")
        sid = manager.add_student("Alice")
        manager.enroll_student(sid, cid)
        with pytest.raises(ValueError, match="between 0 and 100"):
            manager.record_grade(sid, cid, -1)

    def test_record_grade_out_of_range_high(self, manager):
        cid = manager.add_course("Math")
        sid = manager.add_student("Alice")
        manager.enroll_student(sid, cid)
        with pytest.raises(ValueError, match="between 0 and 100"):
            manager.record_grade(sid, cid, 101)

    def test_get_student_grades_success(self, manager):
        cid = manager.add_course("Math")
        sid = manager.add_student("Alice")
        manager.enroll_student(sid, cid)
        manager.record_grade(sid, cid, 90)
        
        grades = manager.get_student_grades(sid)
        assert len(grades) == 1
        assert grades[0]["course_name"] == "Math"
        assert grades[0]["grade"] == 90

    def test_get_student_grades_not_found(self, manager):
        grades = manager.get_student_grades("STU-999")
        assert grades == []

    def test_get_course_average_success(self, manager):
        cid = manager.add_course("Math")
        sid1 = manager.add_student("Alice")
        sid2 = manager.add_student("Bob")
        manager.enroll_student(sid1, cid)
        manager.enroll_student(sid2, cid)
        manager.record_grade(sid1, cid, 80)
        manager.record_grade(sid2, cid, 90)
        
        avg = manager.get_course_average(cid)
        assert avg == 85.0

    def test_get_course_average_no_students(self, manager):
        cid = manager.add_course("Math")
        avg = manager.get_course_average(cid)
        assert avg == 0.0

    def test_get_course_average_not_found(self, manager):
        avg = manager.get_course_average("COURSE-999")
        assert avg is None

    def test_get_student_ranking_success(self, manager):
        cid1 = manager.add_course("Math")
        cid2 = manager.add_course("Physics")
        
        sid1 = manager.add_student("Alice")
        sid2 = manager.add_student("Bob")
        sid3 = manager.add_student("Charlie")
        
        manager.enroll_student(sid1, cid1)
        manager.enroll_student(sid1, cid2)
        manager.enroll_student(sid2, cid1)
        manager.enroll_student(sid2, cid2)
        manager.enroll_student(sid3, cid1)
        manager.enroll_student(sid3, cid2)
        
        manager.record_grade(sid1, cid1, 90)
        manager.record_grade(sid1, cid2, 90)
        manager.record_grade(sid2, cid1, 80)
        manager.record_grade(sid2, cid2, 80)
        manager.record_grade(sid3, cid1, 70)
        manager.record_grade(sid3, cid2, 70)
        
        ranking = manager.get_student_ranking(2)
        assert len(ranking) == 2
        assert ranking[0]["student_id"] == sid1  # Alice has highest avg
        assert ranking[1]["student_id"] == sid2  # Bob has second highest avg

    def test_get_student_ranking_tie_breaker(self, manager):
        cid = manager.add_course("Math")
        
        sid1 = manager.add_student("Zack")
        sid2 = manager.add_student("Adam")
        
        manager.enroll_student(sid1, cid)
        manager.enroll_student(sid2, cid)
        
        manager.record_grade(sid1, cid, 80)
        manager.record_grade(sid2, cid, 80)
        
        ranking = manager.get_student_ranking(2)
        # Same average, so sort by student ID ascending
        # STU-001 (Zack) < STU-002 (Adam) alphabetically/numerically as strings
        assert ranking[0]["student_id"] == sid1  # Zack comes first because STU-001 < STU-002
        assert ranking[0]["student_name"] == "Zack"
        assert ranking[1]["student_id"] == sid2
        assert ranking[1]["student_name"] == "Adam"

    def test_invalid_course_id_format(self, manager):
        manager.add_course("Math")
        with pytest.raises(ValueError, match="Invalid course ID format"):
            manager.enroll_student("STU-001", "BAD-ID")

    def test_invalid_student_id_format(self, manager):
        manager.add_course("Math")
        with pytest.raises(ValueError, match="Invalid student ID format"):
            manager.enroll_student("BAD-ID", "COURSE-001")