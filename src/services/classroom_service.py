"""
Derslik servisi
"""

from typing import List, Optional, Tuple
from src.models.classroom import Classroom, CLASSROOM_TYPES, CLASSROOM_TYPE_MAP
from src.repositories.classroom_repository import ClassroomRepository


class ClassroomService:
    
    def __init__(self):
        self.repository = ClassroomRepository()
    
    def get_all(self) -> List[Classroom]:
        return self.repository.get_all()
    
    def get_by_id(self, classroom_id: int) -> Optional[Classroom]:
        return self.repository.get_by_id(classroom_id)
    
    def get_by_faculty(self, faculty_id: int) -> List[Classroom]:
        return self.repository.get_by_faculty(faculty_id)
    
    def get_by_min_capacity(self, min_capacity: int) -> List[Classroom]:
        return self.repository.get_by_min_capacity(min_capacity)
    
    def get_by_room_type(self, room_type: str) -> List[Classroom]:
        return self.repository.get_by_room_type(room_type)
    
    def get_by_types(self, room_types: List[str]) -> List[Classroom]:
        return self.repository.get_by_types(room_types)
    
    def get_faculties(self) -> List[dict]:
        return self.repository.get_faculties()
    
    def get_exam_suitable(self, room_type: Optional[str] = None) -> List[Classroom]:
        return self.repository.get_exam_suitable_classrooms(room_type)
    
    def get_suitable_with_capacity(self, min_capacity: int = 0, room_type: Optional[str] = None) -> List[Classroom]:
        return self.repository.get_suitable_classrooms(min_capacity, room_type)
    
    def get_room_types(self) -> List[tuple]:
        return CLASSROOM_TYPES
    
    def create(self, name: str, faculty_id: int, capacity: int,
               has_computer: bool = False, is_suitable: bool = True,
               room_type: str = "STANDART") -> Tuple[bool, str, Optional[int]]:
        if not name or not name.strip():
            return False, "Derslik adı gereklidir.", None
        
        if not faculty_id:
            return False, "Fakülte seçimi gereklidir.", None
        
        if capacity <= 0:
            return False, "Kapasite sıfırdan büyük olmalıdır.", None
        
        # Normalize room_type
        normalized_type = room_type.upper()
        if normalized_type not in CLASSROOM_TYPE_MAP:
            normalized_type = "STANDART"
        
        classroom = Classroom(
            name=name.strip(),
            faculty_id=faculty_id,
            capacity=capacity,
            has_computer=has_computer,
            is_suitable=is_suitable,
            room_type=normalized_type
        )
        
        try:
            classroom_id = self.repository.create(classroom)
            return True, "Derslik başarıyla oluşturuldu.", classroom_id
        except Exception as e:
            return False, f"Derslik oluşturulamadı: {str(e)}", None
    
    def update(self, classroom_id: int, name: str, faculty_id: int,
               capacity: int, has_computer: bool, is_suitable: bool = True,
               room_type: str = "STANDART") -> Tuple[bool, str]:

        classroom = self.repository.get_by_id(classroom_id)
        if not classroom:
            return False, "Derslik bulunamadı."
        
        if not name or not name.strip():
            return False, "Derslik adı gereklidir."
        
        if not faculty_id:
            return False, "Fakülte seçimi gereklidir."
        
        if capacity <= 0:
            return False, "Kapasite sıfırdan büyük olmalıdır."
        
        # Normalize room_type
        normalized_type = room_type.upper()
        if normalized_type not in CLASSROOM_TYPE_MAP:
            normalized_type = "STANDART"
        
        classroom.name = name.strip()
        classroom.faculty_id = faculty_id
        classroom.capacity = capacity
        classroom.has_computer = has_computer
        classroom.is_suitable = is_suitable
        classroom.room_type = normalized_type
        
        if self.repository.update(classroom):
            return True, "Derslik başarıyla güncellendi."
        return False, "Derslik güncellenemedi."
    
    def delete(self, classroom_id: int) -> Tuple[bool, str]:

        classroom = self.repository.get_by_id(classroom_id)
        if not classroom:
            return False, "Derslik bulunamadı."
        
        if self.repository.delete(classroom_id):
            return True, "Derslik başarıyla silindi."
        return False, "Derslik silinemedi."
    
    def search(self, keyword: str) -> List[Classroom]:
        if not keyword or not keyword.strip():
            return self.get_all()
        return self.repository.search('name', keyword.strip())
    
    def get_available_for_exam(self, exam_date: str, start_time: str, end_time: str,
                                min_capacity: int = 0, room_type: Optional[str] = None) -> List[Classroom]:
        """Belirtilen tarihte müsait olan derslikleri getirir. ��steğe bağlı oda tipi filtresi."""
        available = self.repository.get_available_for_exam(exam_date, start_time, end_time, room_type)
        if min_capacity > 0:
            available = [c for c in available if c.capacity >= min_capacity]
        return available
    
    def get_count(self) -> int:
        return self.repository.count()
