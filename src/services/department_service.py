"""
Bölüm servisi
"""

from typing import List, Optional, Tuple
from src.models.department import Department
from src.repositories.department_repository import DepartmentRepository


class DepartmentService:
    
    def __init__(self):
        self.repository = DepartmentRepository()
    
    def get_all(self) -> List[Department]:
        return self.repository.get_all_with_faculty()
    
    def get_by_id(self, department_id: int) -> Optional[Department]:
        return self.repository.get_by_id(department_id)
    
    def get_by_code(self, code: str) -> Optional[Department]:
        return self.repository.get_by_code(code)
    
    def get_by_faculty_id(self, faculty_id: int) -> List[Department]:
        return self.repository.get_by_faculty_id(faculty_id)
    
    def create(self, faculty_id: int, name: str, code: str, head_name: str = None) -> Tuple[bool, str, Optional[int]]:
        if not faculty_id:
            return False, "Fakülte seçimi gereklidir.", None
        
        if not name or not name.strip():
            return False, "Bölüm adı gereklidir.", None
        
        if not code or not code.strip():
            return False, "Bölüm kodu gereklidir.", None
        
        existing = self.repository.get_by_code(code.strip().upper())
        if existing:
            return False, "Bu bölüm kodu zaten kullanılıyor.", None
        
        department = Department(
            faculty_id=faculty_id,
            name=name.strip(),
            code=code.strip().upper(),
            head_name=head_name.strip() if head_name else None
        )
        
        try:
            department_id = self.repository.create(department)
            return True, "Bölüm başarıyla oluşturuldu.", department_id
        except Exception as e:
            return False, f"Bölüm oluşturulamadı: {str(e)}", None
    
    def update(self, department_id: int, faculty_id: int, name: str, code: str, head_name: str = None) -> Tuple[bool, str]:
        department = self.repository.get_by_id(department_id)
        if not department:
            return False, "Bölüm bulunamadı."
        
        if not faculty_id:
            return False, "Fakülte seçimi gereklidir."
        
        if not name or not name.strip():
            return False, "Bölüm adı gereklidir."
        
        if not code or not code.strip():
            return False, "Bölüm kodu gereklidir."
        
        existing = self.repository.get_by_code(code.strip().upper())
        if existing and existing.id != department_id:
            return False, "Bu bölüm kodu zaten kullanılıyor."
        
        department.faculty_id = faculty_id
        department.name = name.strip()
        department.code = code.strip().upper()
        department.head_name = head_name.strip() if head_name else None
        
        if self.repository.update(department):
            return True, "Bölüm başarıyla güncellendi."
        return False, "Bölüm güncellenemedi."
    
    def delete(self, department_id: int) -> Tuple[bool, str]:
        department = self.repository.get_by_id(department_id)
        if not department:
            return False, "Bölüm bulunamadı."
        
        if self.repository.delete(department_id):
            return True, "Bölüm başarıyla silindi."
        return False, "Bölüm silinemedi."
    
    def search(self, keyword: str) -> List[Department]:
        if not keyword or not keyword.strip():
            return self.get_all()
        return self.repository.search('name', keyword.strip())
    
    def get_count(self) -> int:
        return self.repository.count()
