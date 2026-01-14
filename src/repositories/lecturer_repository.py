"""
Öğretim görevlisi repository sınıfı
"""

from typing import List, Optional
from src.repositories.base_repository import BaseRepository
from src.models.lecturer import Lecturer


class LecturerRepository(BaseRepository[Lecturer]):
    
    def __init__(self):
        super().__init__()
        self.table_name = "lecturers"
    
    def _row_to_entity(self, row: tuple, columns: List[str]) -> Lecturer:
        data = dict(zip(columns, row))
        return Lecturer.from_dict(data)
    
    def _entity_to_values(self, entity: Lecturer) -> tuple:
        return (
            entity.department_id,
            entity.first_name,
            entity.last_name,
            entity.title,
            entity.email,
            entity.available_days
        )
    
    def create(self, lecturer: Lecturer) -> int:
        query = """
            INSERT INTO lecturers (department_id, first_name, last_name, title, email, available_days)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        values = self._entity_to_values(lecturer)
        return self._execute_non_query(query, values, return_id=True)
    
    def update(self, lecturer: Lecturer) -> bool:
        query = """
            UPDATE lecturers
            SET department_id = %s, first_name = %s, last_name = %s, title = %s,
                email = %s, available_days = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        values = self._entity_to_values(lecturer) + (lecturer.id,)
        try:
            self._execute_non_query(query, values)
            return True
        except Exception:
            return False
    
    def get_by_department_id(self, department_id: int) -> List[Lecturer]:
        query = """
            SELECT l.*, d.name as department_name, f.name as faculty_name
            FROM lecturers l
            LEFT JOIN departments d ON l.department_id = d.id
            LEFT JOIN faculties f ON d.faculty_id = f.id
            WHERE l.department_id = %s
            ORDER BY l.last_name, l.first_name
        """
        rows, columns = self._execute_query(query, (department_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_all_with_details(self) -> List[Lecturer]:
        query = """
            SELECT l.*, d.name as department_name, f.name as faculty_name
            FROM lecturers l
            LEFT JOIN departments d ON l.department_id = d.id
            LEFT JOIN faculties f ON d.faculty_id = f.id
            ORDER BY f.name, d.name, l.last_name, l.first_name
        """
        rows, columns = self._execute_query(query)
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_email(self, email: str) -> Optional[Lecturer]:
        query = """
            SELECT l.*, d.name as department_name, f.name as faculty_name
            FROM lecturers l
            LEFT JOIN departments d ON l.department_id = d.id
            LEFT JOIN faculties f ON d.faculty_id = f.id
            WHERE l.email = %s
        """
        rows, columns = self._execute_query(query, (email,))
        if rows:
            return self._row_to_entity(rows[0], columns)
        return None
    
    def get_available_on_day(self, day: str) -> List[Lecturer]:
        query = """
            SELECT l.*, d.name as department_name, f.name as faculty_name
            FROM lecturers l
            LEFT JOIN departments d ON l.department_id = d.id
            LEFT JOIN faculties f ON d.faculty_id = f.id
            WHERE %s = ANY(l.available_days)
            ORDER BY l.last_name, l.first_name
        """
        rows, columns = self._execute_query(query, (day,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def update_available_days(self, lecturer_id: int, available_days: List[str]) -> bool:
        query = """
            UPDATE lecturers
            SET available_days = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        try:
            self._execute_non_query(query, (available_days, lecturer_id))
            return True
        except Exception:
            return False
