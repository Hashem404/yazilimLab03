"""
Derslik repository sınıfı
"""

from typing import List, Optional
from src.repositories.base_repository import BaseRepository
from src.models.classroom import Classroom, CLASSROOM_TYPE_MAP, CLASSROOM_TYPES


class ClassroomRepository(BaseRepository[Classroom]):
    
    def __init__(self):
        super().__init__()
        self.table_name = "classrooms"
    
    def _row_to_entity(self, row: tuple, columns: List[str]) -> Classroom:
        data = dict(zip(columns, row))
        return Classroom.from_dict(data)
    
    def _entity_to_values(self, entity: Classroom) -> tuple:
        return (
            entity.name,
            entity.faculty_id,
            entity.capacity,
            entity.has_computer,
            entity.is_suitable,
            entity.room_type
        )
    
    def get_all(self) -> List[Classroom]:
        query = """
            SELECT c.id, c.name, c.faculty_id, c.capacity, c.has_computer, c.is_suitable, c.room_type,
                   f.name as faculty_name
            FROM classrooms c
            LEFT JOIN faculties f ON c.faculty_id = f.id
            ORDER BY f.name, c.name
        """
        rows, columns = self._execute_query(query)
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_id(self, id: int) -> Optional[Classroom]:
        query = """
            SELECT c.id, c.name, c.faculty_id, c.capacity, c.has_computer, c.is_suitable, c.room_type,
                   f.name as faculty_name
            FROM classrooms c
            LEFT JOIN faculties f ON c.faculty_id = f.id
            WHERE c.id = %s
        """
        rows, columns = self._execute_query(query, (id,))
        if rows:
            return self._row_to_entity(rows[0], columns)
        return None
    
    def create(self, classroom: Classroom) -> int:
        query = """
            INSERT INTO classrooms (name, faculty_id, capacity, has_computer, is_suitable, room_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        values = self._entity_to_values(classroom)
        return self._execute_non_query(query, values, return_id=True)
    
    def update(self, classroom: Classroom) -> bool:
        query = """
            UPDATE classrooms
            SET name = %s, faculty_id = %s, capacity = %s, has_computer = %s, is_suitable = %s, room_type = %s
            WHERE id = %s
        """
        values = self._entity_to_values(classroom) + (classroom.id,)
        try:
            self._execute_non_query(query, values)
            return True
        except Exception:
            return False
    
    def get_by_faculty(self, faculty_id: int) -> List[Classroom]:
        query = """
            SELECT c.id, c.name, c.faculty_id, c.capacity, c.has_computer, c.is_suitable, c.room_type,
                   f.name as faculty_name
            FROM classrooms c
            LEFT JOIN faculties f ON c.faculty_id = f.id
            WHERE c.faculty_id = %s
            ORDER BY c.name
        """
        rows, columns = self._execute_query(query, (faculty_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_room_type(self, room_type: str) -> List[Classroom]:
        """Belirli bir tipteki derslikleri getirir"""
        normalized_type = room_type.upper()
        if normalized_type not in CLASSROOM_TYPE_MAP:
            normalized_type = 'STANDART'
        
        query = """
            SELECT c.id, c.name, c.faculty_id, c.capacity, c.has_computer, c.is_suitable, c.room_type,
                   f.name as faculty_name
            FROM classrooms c
            LEFT JOIN faculties f ON c.faculty_id = f.id
            WHERE c.room_type = %s
            ORDER BY c.capacity DESC
        """
        rows, columns = self._execute_query(query, (normalized_type,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_types(self, room_types: List[str]) -> List[Classroom]:
        """Birden fazla tipteki derslikleri getirir"""
        normalized_types = [rt.upper() for rt in room_types if rt.upper() in CLASSROOM_TYPE_MAP]
        if not normalized_types:
            normalized_types = ['STANDART']
        
        placeholders = ','.join(['%s'] * len(normalized_types))
        query = f"""
            SELECT c.id, c.name, c.faculty_id, c.capacity, c.has_computer, c.is_suitable, c.room_type,
                   f.name as faculty_name
            FROM classrooms c
            LEFT JOIN faculties f ON c.faculty_id = f.id
            WHERE c.room_type IN ({placeholders})
            ORDER BY c.capacity DESC
        """
        rows, columns = self._execute_query(query, tuple(normalized_types))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_min_capacity(self, min_capacity: int) -> List[Classroom]:
        query = """
            SELECT c.id, c.name, c.faculty_id, c.capacity, c.has_computer, c.is_suitable, c.room_type,
                   f.name as faculty_name
            FROM classrooms c
            LEFT JOIN faculties f ON c.faculty_id = f.id
            WHERE c.capacity >= %s
            ORDER BY c.capacity
        """
        rows, columns = self._execute_query(query, (min_capacity,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_available_for_exam(self, exam_date: str, start_time: str, end_time: str, room_type: Optional[str] = None) -> List[Classroom]:
        """Belirtilen tarihte müsait olan derslikleri getirir. İsteğe bağlı oda tipi filtresi."""
        type_filter = ""
        params = [exam_date, start_time, start_time, end_time, end_time, start_time, end_time]
        
        if room_type and room_type.upper() in CLASSROOM_TYPE_MAP:
            type_filter = " AND c.room_type = %s"
            params.append(room_type.upper())
        elif room_type and room_type.upper() == 'ANY':
            type_filter = ""
        else:
            # Varsayılan olarak STANDART tipini filtrele
            if room_type is None:
                pass  # Tüm tipleri getir
            else:
                type_filter = " AND c.room_type = %s"
                params.append('STANDART')
        
        query = f"""
            SELECT c.id, c.name, c.faculty_id, c.capacity, c.has_computer, c.is_suitable, c.room_type,
                   f.name as faculty_name
            FROM classrooms c
            LEFT JOIN faculties f ON c.faculty_id = f.id
            WHERE c.is_suitable = TRUE
            {type_filter}
            AND c.id NOT IN (
                SELECT es.classroom_id FROM exam_schedule es
                WHERE es.exam_date = %s
                AND es.status != 'cancelled'
                AND (
                    (es.start_time <= %s AND es.end_time > %s)
                    OR (es.start_time < %s AND es.end_time >= %s)
                    OR (es.start_time >= %s AND es.end_time <= %s)
                )
            )
            ORDER BY c.capacity
        """
        rows, columns = self._execute_query(query, tuple(params))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_faculties(self) -> List[dict]:
        query = """
            SELECT DISTINCT f.id, f.name
            FROM classrooms c
            JOIN faculties f ON c.faculty_id = f.id
            ORDER BY f.name
        """
        rows, _ = self._execute_query(query)
        return [{'id': row[0], 'name': row[1]} for row in rows]
    
    def get_suitable_classrooms(self, min_capacity: int = 0, room_type: Optional[str] = None) -> List[Classroom]:
        """Kapasite ve oda tipine göre uygun derslikleri getirir"""
        type_filter = ""
        params = [min_capacity]
        
        if room_type and room_type.upper() in CLASSROOM_TYPE_MAP:
            type_filter = " AND c.room_type = %s"
            params.append(room_type.upper())
        
        query = f"""
            SELECT c.id, c.name, c.faculty_id, c.capacity, c.has_computer, c.is_suitable, c.room_type,
                   f.name as faculty_name
            FROM classrooms c
            LEFT JOIN faculties f ON c.faculty_id = f.id
            WHERE c.is_suitable = TRUE AND c.capacity >= %s{type_filter}
            ORDER BY c.capacity
        """
        rows, columns = self._execute_query(query, tuple(params))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_exam_suitable_classrooms(self, room_type: Optional[str] = None) -> List[Classroom]:
        """Sınav için uygun derslikleri getirir. İsteğe bağlı oda tipi filtresi."""
        type_filter = ""
        params = []
        
        if room_type and room_type.upper() in CLASSROOM_TYPE_MAP:
            type_filter = " WHERE c.room_type = %s"
            params.append(room_type.upper())
        
        query = f"""
            SELECT c.id, c.name, c.faculty_id, c.capacity, c.has_computer, c.is_suitable, c.room_type,
                   f.name as faculty_name
            FROM classrooms c
            LEFT JOIN faculties f ON c.faculty_id = f.id
            {type_filter}
            AND c.is_suitable = TRUE
            ORDER BY f.name, c.name
        """
        rows, columns = self._execute_query(query, tuple(params))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_room_types(self) -> List[dict]:
        """Mevcut derslik tiplerini döndürür"""
        query = """
            SELECT DISTINCT room_type, COUNT(*) as count
            FROM classrooms
            WHERE room_type IS NOT NULL AND room_type != ''
            GROUP BY room_type
            ORDER BY room_type
        """
        rows, _ = self._execute_query(query)
        return [{'room_type': row[0], 'count': row[1]} for row in rows]
    
    def get_by_name(self, name: str) -> Optional[Classroom]:
        """Derslik adına göre derslik getirir"""
        query = """
            SELECT c.id, c.name, c.faculty_id, c.capacity, c.has_computer, c.is_suitable, c.room_type,
                   f.name as faculty_name
            FROM classrooms c
            LEFT JOIN faculties f ON c.faculty_id = f.id
            WHERE c.name = %s
        """
        rows, columns = self._execute_query(query, (name,))
        if rows:
            return self._row_to_entity(rows[0], columns)
        return None
    
    def get_available_classrooms(self, exam_date: str, start_time: str, end_time: str, room_type: Optional[str] = None) -> List[Classroom]:
        """Belirtilen zaman diliminde müsait derslikleri getirir. İsteğe bağlı oda tipi filtresi."""
        type_filter = ""
        params = [exam_date, end_time, start_time, end_time, start_time, start_time, end_time]
        
        if room_type and room_type.upper() in CLASSROOM_TYPE_MAP:
            type_filter = " AND c.room_type = %s"
            params.append(room_type.upper())
        
        query = f"""
            SELECT c.id, c.name, c.faculty_id, c.capacity, c.has_computer, c.is_suitable, c.room_type,
                   f.name as faculty_name
            FROM classrooms c
            LEFT JOIN faculties f ON c.faculty_id = f.id
            WHERE c.is_suitable = TRUE
            {type_filter}
            AND c.id NOT IN (
                SELECT es.classroom_id FROM exam_schedule es
                WHERE es.exam_date = %s
                AND es.status != 'cancelled'
                AND (
                    (es.start_time < %s AND es.end_time > %s)
                    OR (es.start_time < %s AND es.end_time > %s)
                    OR (es.start_time >= %s AND es.end_time <= %s)
                )
            )
            ORDER BY f.name, c.name
        """
        rows, columns = self._execute_query(query, tuple(params))
        return [self._row_to_entity(row, columns) for row in rows]
