"""
Sınav programı repository sınıfı
"""

from typing import List, Optional
from datetime import date
from src.repositories.base_repository import BaseRepository
from src.models.exam_schedule import ExamSchedule


class ExamScheduleRepository(BaseRepository[ExamSchedule]):
    
    def __init__(self):
        super().__init__()
        self.table_name = "exam_schedule"
    
    def _row_to_entity(self, row: tuple, columns: List[str]) -> ExamSchedule:
        data = dict(zip(columns, row))
        return ExamSchedule.from_dict(data)
    
    def _entity_to_values(self, entity: ExamSchedule) -> tuple:
        return (
            entity.course_id,
            entity.classroom_id,
            entity.exam_date,
            entity.start_time,
            entity.end_time,
            entity.exam_type,
            entity.status,
            entity.notes
        )
    
    def create(self, exam_schedule: ExamSchedule) -> int:
        query = """
            INSERT INTO exam_schedule (course_id, classroom_id, exam_date, start_time, end_time, exam_type, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        values = self._entity_to_values(exam_schedule)
        return self._execute_non_query(query, values, return_id=True)
    
    def update(self, exam_schedule: ExamSchedule) -> bool:
        query = """
            UPDATE exam_schedule
            SET course_id = %s, classroom_id = %s, exam_date = %s, start_time = %s,
                end_time = %s, exam_type = %s, status = %s, notes = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        values = self._entity_to_values(exam_schedule) + (exam_schedule.id,)
        try:
            self._execute_non_query(query, values)
            return True
        except Exception:
            return False
    
    def get_by_date(self, exam_date: date) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE es.exam_date = %s
            ORDER BY es.start_time, f.name, cl.name
        """
        rows, columns = self._execute_query(query, (exam_date,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE es.exam_date BETWEEN %s AND %s
            ORDER BY es.exam_date, es.start_time
        """
        rows, columns = self._execute_query(query, (start_date, end_date))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_course_id(self, course_id: int) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name,
                   cl.name as classroom_name, f.name as faculty_name
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            WHERE es.course_id = %s
            ORDER BY es.exam_date, es.start_time
        """
        rows, columns = self._execute_query(query, (course_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_classroom_id(self, classroom_id: int) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name,
                   cl.name as classroom_name, f.name as faculty_name
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            WHERE es.classroom_id = %s
            ORDER BY es.exam_date, es.start_time
        """
        rows, columns = self._execute_query(query, (classroom_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_all_with_details(self) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            ORDER BY es.exam_date, es.start_time
        """
        rows, columns = self._execute_query(query)
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_department_id(self, department_id: int) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE c.department_id = %s
            ORDER BY es.exam_date, es.start_time
        """
        rows, columns = self._execute_query(query, (department_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def check_conflict(self, classroom_id: int, exam_date: date, start_time: str, end_time: str, exclude_id: int = None) -> bool:
        query = """
            SELECT EXISTS(
                SELECT 1 FROM exam_schedule
                WHERE classroom_id = %s
                AND exam_date = %s
                AND status != 'cancelled'
                AND id != COALESCE(%s, -1)
                AND (
                    (start_time <= %s AND end_time > %s)
                    OR (start_time < %s AND end_time >= %s)
                    OR (start_time >= %s AND end_time <= %s)
                )
            )
        """
        rows, _ = self._execute_query(
            query,
            (classroom_id, exam_date, exclude_id, start_time, start_time, end_time, end_time, start_time, end_time)
        )
        return rows[0][0] if rows else False
    
    def update_status(self, exam_id: int, status: str) -> bool:
        query = "UPDATE exam_schedule SET status = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        try:
            self._execute_non_query(query, (status, exam_id))
            return True
        except Exception:
            return False
    
    def get_by_classroom_and_date(self, classroom_id: int, exam_date: date) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE es.classroom_id = %s
            AND es.exam_date = %s
            AND es.status != 'cancelled'
            ORDER BY es.start_time
        """
        rows, columns = self._execute_query(query, (classroom_id, exam_date))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_department_and_date(self, department_id: int, exam_date: date) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name, c.year as course_year
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE c.department_id = %s
            AND es.exam_date = %s
            AND es.status != 'cancelled'
            ORDER BY es.start_time
        """
        rows, columns = self._execute_query(query, (department_id, exam_date))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_lecturer_and_date(self, lecturer_id: int, exam_date: date) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE c.lecturer_id = %s
            AND es.exam_date = %s
            AND es.status != 'cancelled'
            ORDER BY es.start_time
        """
        rows, columns = self._execute_query(query, (lecturer_id, exam_date))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def delete_all(self) -> int:
        query = "DELETE FROM exam_schedule"
        return self._execute_non_query(query)
    
    def delete_planned(self) -> int:
        query = "DELETE FROM exam_schedule WHERE status = 'planned'"
        return self._execute_non_query(query)
    
    def get_by_status(self, status: str) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE es.status = %s
            ORDER BY es.exam_date, es.start_time
        """
        rows, columns = self._execute_query(query, (status,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def check_course_exam_exists(self, course_id: int, exam_type: str, exclude_id: int = None, exclude_ids: list = None) -> bool:
        if exclude_ids is None:
            exclude_ids = [exclude_id] if exclude_id else []
        
        if exclude_ids:
            placeholders = ', '.join(['%s'] * len(exclude_ids))
            query = f"""
                SELECT EXISTS(
                    SELECT 1 FROM exam_schedule
                    WHERE course_id = %s
                    AND exam_type = %s
                    AND status != 'cancelled'
                    AND id NOT IN ({placeholders})
                )
            """
            params = [course_id, exam_type] + exclude_ids
            rows, _ = self._execute_query(query, tuple(params))
        else:
            query = """
                SELECT EXISTS(
                    SELECT 1 FROM exam_schedule
                    WHERE course_id = %s
                    AND exam_type = %s
                    AND status != 'cancelled'
                )
            """
            rows, _ = self._execute_query(query, (course_id, exam_type))
        
        return rows[0][0] if rows else False
    
    def check_student_conflict(
        self,
        department_id: int,
        course_year: int,
        exam_date: date,
        start_time: str,
        end_time: str,
        exclude_course_id: int = None,
        exclude_id: int = None
    ) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name, c.year as course_year
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE c.department_id = %s
            AND c.year = %s
            AND es.exam_date = %s
            AND es.status != 'cancelled'
            AND es.id != COALESCE(%s, -1)
            AND c.id != COALESCE(%s, -1)
            AND (
                (es.start_time <= %s AND es.end_time > %s)
                OR (es.start_time < %s AND es.end_time >= %s)
                OR (es.start_time >= %s AND es.end_time <= %s)
            )
            ORDER BY es.start_time
        """
        rows, columns = self._execute_query(
            query,
            (department_id, course_year, exam_date, exclude_id, exclude_course_id,
             start_time, start_time, end_time, end_time, start_time, end_time)
        )
        return [self._row_to_entity(row, columns) for row in rows]
    
    def check_lecturer_conflict(
        self,
        lecturer_id: int,
        exam_date: date,
        start_time: str,
        end_time: str,
        exclude_id: int = None
    ) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE c.lecturer_id = %s
            AND es.exam_date = %s
            AND es.status != 'cancelled'
            AND es.id != COALESCE(%s, -1)
            AND (
                (es.start_time <= %s AND es.end_time > %s)
                OR (es.start_time < %s AND es.end_time >= %s)
                OR (es.start_time >= %s AND es.end_time <= %s)
            )
            ORDER BY es.start_time
        """
        rows, columns = self._execute_query(
            query,
            (lecturer_id, exam_date, exclude_id,
             start_time, start_time, end_time, end_time, start_time, end_time)
        )
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_faculty_id(self, faculty_id: int) -> List[ExamSchedule]:
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE d.faculty_id = %s
            ORDER BY es.exam_date, es.start_time
        """
        rows, columns = self._execute_query(query, (faculty_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    # ==================== KULLANICI BAZLI FİLTRELEME ====================
    
    def get_by_student_id(self, student_id: int) -> List[ExamSchedule]:
        """
        Belirli bir öğrencinin aldığı derslerin sınav programını döndürür.
        student_courses tablosu üzerinden dersleri bulur.
        """
        query = """
            SELECT DISTINCT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name
            FROM exam_schedule es
            INNER JOIN student_courses sc ON es.course_id = sc.course_id
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE sc.student_id = %s
              AND sc.is_active = TRUE
              AND es.status != 'cancelled'
            ORDER BY es.exam_date, es.start_time
        """
        rows, columns = self._execute_query(query, (student_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_student_number(self, student_number: str) -> List[ExamSchedule]:
        """
        Öğrenci numarasına göre sınav programını döndürür.
        """
        query = """
            SELECT DISTINCT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name
            FROM exam_schedule es
            INNER JOIN student_courses sc ON es.course_id = sc.course_id
            INNER JOIN students s ON sc.student_id = s.id
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE s.student_number = %s
              AND sc.is_active = TRUE
              AND s.is_active = TRUE
              AND es.status != 'cancelled'
            ORDER BY es.exam_date, es.start_time
        """
        rows, columns = self._execute_query(query, (student_number,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_lecturer_id_all(self, lecturer_id: int) -> List[ExamSchedule]:
        """
        Belirli bir öğretim üyesinin verdiği derslerin tüm sınavlarını döndürür.
        """
        query = """
            SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
                   cl.name as classroom_name, f.name as faculty_name,
                   CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
                   d.name as department_name
            FROM exam_schedule es
            LEFT JOIN courses c ON es.course_id = c.id
            LEFT JOIN classrooms cl ON es.classroom_id = cl.id
            LEFT JOIN faculties f ON cl.faculty_id = f.id
            LEFT JOIN lecturers l ON c.lecturer_id = l.id
            LEFT JOIN departments d ON c.department_id = d.id
            WHERE c.lecturer_id = %s
              AND es.status != 'cancelled'
            ORDER BY es.exam_date, es.start_time
        """
        rows, columns = self._execute_query(query, (lecturer_id,))
        return [self._row_to_entity(row, columns) for row in rows]
