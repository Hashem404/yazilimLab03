"""
Ders repository sınıfı
"""

from typing import List, Optional
from src.repositories.base_repository import BaseRepository
from src.models.course import Course


class CourseRepository(BaseRepository[Course]):
    
    def __init__(self):
        super().__init__()
        self.table_name = "courses"
    
    def _row_to_entity(self, row: tuple, columns: List[str]) -> Course:
        data = dict(zip(columns, row))
        return Course.from_dict(data)
    
    def _entity_to_values(self, entity: Course) -> tuple:
        return (
            entity.department_id,
            entity.lecturer_id,
            entity.code,
            entity.name,
            entity.credit,
            entity.year,
            entity.semester,
            entity.period,
            entity.theory_hours,
            entity.lab_hours,
            entity.course_type,
            entity.description,
            entity.student_count,
            entity.lecturer_count,
            entity.exam_type,
            entity.exam_duration,
            entity.has_exam,
            entity.required_room_type
        )
    
    def create(self, course: Course) -> int:
        query = """
            INSERT INTO courses (department_id, lecturer_id, code, name, credit, year, semester,
                                 period, theory_hours, lab_hours, course_type, description,
                                 student_count, lecturer_count, exam_type, exam_duration, has_exam,
                                 required_room_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        values = self._entity_to_values(course)
        return self._execute_non_query(query, values, return_id=True)
    
    def update(self, course: Course) -> bool:
        query = """
            UPDATE courses
            SET department_id = %s, lecturer_id = %s, code = %s, name = %s, credit = %s,
                year = %s, semester = %s, period = %s, theory_hours = %s, lab_hours = %s,
                course_type = %s, description = %s, student_count = %s, lecturer_count = %s,
                exam_type = %s, exam_duration = %s, has_exam = %s, required_room_type = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        values = self._entity_to_values(course) + (course.id,)
        try:
            self._execute_non_query(query, values)
            return True
        except Exception:
            return False
    
    def get_by_code(self, code: str) -> Optional[Course]:
        query = "SELECT * FROM courses WHERE code = %s"
        rows, columns = self._execute_query(query, (code,))
        if rows:
            return self._row_to_entity(rows[0], columns)
        return None
    
    def get_by_department_id(self, department_id: int) -> List[Course]:
        query = """
            SELECT c.*, d.name as department_name, 
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name
            FROM courses c
            LEFT JOIN departments d ON c.department_id = d.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            WHERE c.department_id = %s
            ORDER BY c.year, c.semester, c.code
        """
        rows, columns = self._execute_query(query, (department_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_lecturer_id(self, lecturer_id: int) -> List[Course]:
        query = """
            SELECT c.*, d.name as department_name
            FROM courses c
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE c.lecturer_id = %s
            ORDER BY c.code
        """
        rows, columns = self._execute_query(query, (lecturer_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_all_with_details(self) -> List[Course]:
        query = """
            SELECT c.*, d.name as department_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   f.name as faculty_name
            FROM courses c
            LEFT JOIN departments d ON c.department_id = d.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN faculties f ON d.faculty_id = f.id
            ORDER BY f.name, d.name, c.year, c.semester, c.code
        """
        rows, columns = self._execute_query(query)
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_year_semester(self, year: int, semester: int) -> List[Course]:
        query = """
            SELECT c.*, d.name as department_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name
            FROM courses c
            LEFT JOIN departments d ON c.department_id = d.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            WHERE c.year = %s AND c.semester = %s
            ORDER BY d.name, c.code
        """
        rows, columns = self._execute_query(query, (year, semester))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_unscheduled_courses(self, exam_type: str = None) -> List[Course]:
 
        if exam_type:
            query = """
                SELECT c.*, d.name as department_name,
                       CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                       f.name as faculty_name
                FROM courses c
                LEFT JOIN departments d ON c.department_id = d.id
                LEFT JOIN lecturers l ON c.lecturer_id = l.id
                LEFT JOIN faculties f ON d.faculty_id = f.id
                WHERE c.id NOT IN (
                    SELECT DISTINCT course_id FROM exam_schedule
                    WHERE status != 'cancelled' AND exam_type = %s
                )
                AND c.has_exam = TRUE
                AND c.exam_duration > 0
                ORDER BY f.name, d.name, c.year, c.semester, c.code
            """
            rows, columns = self._execute_query(query, (exam_type,))
        else:
            query = """
                SELECT c.*, d.name as department_name,
                       CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                       f.name as faculty_name
                FROM courses c
                LEFT JOIN departments d ON c.department_id = d.id
                LEFT JOIN lecturers l ON c.lecturer_id = l.id
                LEFT JOIN faculties f ON d.faculty_id = f.id
                WHERE c.id NOT IN (
                    SELECT DISTINCT course_id FROM exam_schedule
                    WHERE status != 'cancelled'
                )
                AND c.has_exam = TRUE
                AND c.exam_duration > 0
                ORDER BY f.name, d.name, c.year, c.semester, c.code
            """
            rows, columns = self._execute_query(query)
        return [self._row_to_entity(row, columns) for row in rows]
