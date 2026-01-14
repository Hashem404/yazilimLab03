"""
Bölüm repository sınıfı
"""

from typing import List, Optional
from src.repositories.base_repository import BaseRepository
from src.models.department import Department


class DepartmentRepository(BaseRepository[Department]):
    
    def __init__(self):
        super().__init__()
        self.table_name = "departments"
    
    def _row_to_entity(self, row: tuple, columns: List[str]) -> Department:
        data = dict(zip(columns, row))
        return Department.from_dict(data)
    
    def _entity_to_values(self, entity: Department) -> tuple:
        return (
            entity.faculty_id,
            entity.name,
            entity.code,
            entity.head_name
        )
    
    def create(self, department: Department) -> int:
        query = """
            INSERT INTO departments (faculty_id, name, code, head_name)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        values = self._entity_to_values(department)
        return self._execute_non_query(query, values, return_id=True)
    
    def update(self, department: Department) -> bool:
        query = """
            UPDATE departments
            SET faculty_id = %s, name = %s, code = %s, head_name = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        values = self._entity_to_values(department) + (department.id,)
        try:
            self._execute_non_query(query, values)
            return True
        except Exception:
            return False
    
    def get_by_code(self, code: str) -> Optional[Department]:
        query = "SELECT * FROM departments WHERE code = %s"
        rows, columns = self._execute_query(query, (code,))
        if rows:
            return self._row_to_entity(rows[0], columns)
        return None
    
    def get_by_faculty_id(self, faculty_id: int) -> List[Department]:
        query = """
            SELECT d.*, f.name as faculty_name
            FROM departments d
            LEFT JOIN faculties f ON d.faculty_id = f.id
            WHERE d.faculty_id = %s
            ORDER BY d.name
        """
        rows, columns = self._execute_query(query, (faculty_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_all_with_faculty(self) -> List[Department]:
        query = """
            SELECT d.*, f.name as faculty_name
            FROM departments d
            LEFT JOIN faculties f ON d.faculty_id = f.id
            ORDER BY f.name, d.name
        """
        rows, columns = self._execute_query(query)
        return [self._row_to_entity(row, columns) for row in rows]
