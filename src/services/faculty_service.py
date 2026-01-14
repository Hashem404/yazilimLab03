"""
Fakülte servisi
"""

from typing import List, Optional, Tuple
from src.models.faculty import Faculty
from src.repositories.faculty_repository import FacultyRepository


class FacultyService:
    
    def __init__(self):
        self.repository = FacultyRepository()
    
    def get_all(self) -> List[Faculty]:
        return self.repository.get_all_active()
    
    def get_by_id(self, faculty_id: int) -> Optional[Faculty]:
        return self.repository.get_by_id(faculty_id)
    
    def get_by_code(self, code: str) -> Optional[Faculty]:
        return self.repository.get_by_code(code)
    
    def create(self, name: str, code: str, dean_name: str = None) -> Tuple[bool, str, Optional[int]]:
        if not name or not name.strip():
            return False, "Fakülte adı gereklidir.", None
        
        if not code or not code.strip():
            return False, "Fakülte kodu gereklidir.", None
        
        existing = self.repository.get_by_code(code.strip().upper())
        if existing:
            return False, "Bu fakülte kodu zaten kullanılıyor.", None
        
        faculty = Faculty(
            name=name.strip(),
            code=code.strip().upper(),
            dean_name=dean_name.strip() if dean_name else None
        )
        
        try:
            faculty_id = self.repository.create(faculty)
            return True, "Fakülte başarıyla oluşturuldu.", faculty_id
        except Exception as e:
            return False, f"Fakülte oluşturulamadı: {str(e)}", None
    
    def update(self, faculty_id: int, name: str, code: str, dean_name: str = None) -> Tuple[bool, str]:
        faculty = self.repository.get_by_id(faculty_id)
        if not faculty:
            return False, "Fakülte bulunamadı."
        
        if not name or not name.strip():
            return False, "Fakülte adı gereklidir."
        
        if not code or not code.strip():
            return False, "Fakülte kodu gereklidir."
        
        existing = self.repository.get_by_code(code.strip().upper())
        if existing and existing.id != faculty_id:
            return False, "Bu fakülte kodu zaten kullanılıyor."
        
        faculty.name = name.strip()
        faculty.code = code.strip().upper()
        faculty.dean_name = dean_name.strip() if dean_name else None
        
        if self.repository.update(faculty):
            return True, "Fakülte başarıyla güncellendi."
        return False, "Fakülte güncellenemedi."
    
    def delete(self, faculty_id: int) -> Tuple[bool, str]:
        faculty = self.repository.get_by_id(faculty_id)
        if not faculty:
            return False, "Fakülte bulunamadı."
        if self.repository.delete(faculty_id):
            return True, "Fakülte başarıyla silindi."
        return False, "Fakülte silinemedi."
    
    def search(self, keyword: str) -> List[Faculty]:
        if not keyword or not keyword.strip():
            return self.get_all()
        return self.repository.search('name', keyword.strip())
    
    def get_count(self) -> int:
        return self.repository.count()
