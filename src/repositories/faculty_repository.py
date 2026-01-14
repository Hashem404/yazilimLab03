"""
Fakülte repository sınıfı
"""

from typing import List, Optional
from src.repositories.base_repository import BaseRepository
from src.models.faculty import Faculty


class FacultyRepository(BaseRepository[Faculty]):
    
    def __init__(self):
        super().__init__()
        self.table_name = "faculties"
    
    def _row_to_entity(self, row: tuple, columns: List[str]) -> Faculty:
        data = dict(zip(columns, row))
        return Faculty.from_dict(data)
    
    def _entity_to_values(self, entity: Faculty) -> tuple:
        return (
            entity.name,
            entity.code,
            entity.dean_name
        )
    
    def create(self, faculty: Faculty) -> int:
        query = """
            INSERT INTO faculties (name, code, dean_name)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        values = self._entity_to_values(faculty)
        return self._execute_non_query(query, values, return_id=True)
    
    def update(self, faculty: Faculty) -> bool:
        query = """
            UPDATE faculties
            SET name = %s, code = %s, dean_name = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        values = self._entity_to_values(faculty) + (faculty.id,)
        try:
            self._execute_non_query(query, values)
            return True
        except Exception:
            return False
    
    def get_by_code(self, code: str) -> Optional[Faculty]:
        query = "SELECT * FROM faculties WHERE code = %s"
        rows, columns = self._execute_query(query, (code,))
        if rows:
            return self._row_to_entity(rows[0], columns)
        return None
    
    def get_all_active(self) -> List[Faculty]:
        query = "SELECT * FROM faculties ORDER BY name"
        rows, columns = self._execute_query(query)
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_with_departments(self) -> List[dict]:
        query = """
            SELECT f.id, f.name as faculty_name, f.code as faculty_code,
                   d.id as department_id, d.name as department_name, d.code as department_code
            FROM faculties f
            LEFT JOIN departments d ON f.id = d.faculty_id
            ORDER BY f.name, d.name
        """
        rows, columns = self._execute_query(query)
        
        faculties_dict = {}
        for row in rows:
            data = dict(zip(columns, row))
            faculty_id = data['id']
            
            if faculty_id not in faculties_dict:
                faculties_dict[faculty_id] = {
                    'id': faculty_id,
                    'name': data['faculty_name'],
                    'code': data['faculty_code'],
                    'departments': []
                }
            
            if data['department_id']:
                faculties_dict[faculty_id]['departments'].append({
                    'id': data['department_id'],
                    'name': data['department_name'],
                    'code': data['department_code']
                })
        
        return list(faculties_dict.values())
