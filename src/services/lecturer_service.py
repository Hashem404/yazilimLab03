"""
Öğretim görevlisi servisi
"""

import re
from typing import List, Optional, Tuple
from src.models.lecturer import Lecturer, DEFAULT_AVAILABLE_DAYS, ALL_WEEKDAYS
from src.repositories.lecturer_repository import LecturerRepository


def normalize_turkish_chars(text: str) -> str:
    replacements = {
        'ı': 'i', 'İ': 'i', 'ğ': 'g', 'Ğ': 'g',
        'ü': 'u', 'Ü': 'u', 'ş': 's', 'Ş': 's',
        'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c'
    }
    for tr_char, ascii_char in replacements.items():
        text = text.replace(tr_char, ascii_char)
    return text.lower()


def generate_email(first_name: str, last_name: str) -> str:
    first = normalize_turkish_chars(first_name.strip())
    last = normalize_turkish_chars(last_name.strip())
    first = re.sub(r'[^a-z]', '', first)
    last = re.sub(r'[^a-z]', '', last)
    return f"{first}.{last}@kstu.edu.tr"


class LecturerService:    
    def __init__(self):
        self.repository = LecturerRepository()
    
    def get_all(self) -> List[Lecturer]:
        return self.repository.get_all_with_details()
    
    def get_by_id(self, lecturer_id: int) -> Optional[Lecturer]:
        return self.repository.get_by_id(lecturer_id)
    
    def get_by_department_id(self, department_id: int) -> List[Lecturer]:
        return self.repository.get_by_department_id(department_id)
    
    def get_by_email(self, email: str) -> Optional[Lecturer]:
        return self.repository.get_by_email(email)
    
    def get_available_on_day(self, day: str) -> List[Lecturer]:
        return self.repository.get_available_on_day(day)
    
    def create(self, department_id: int, first_name: str, last_name: str, title: str,
               email: str = None, available_days: List[str] = None) -> Tuple[bool, str, Optional[int]]:
        if not department_id:
            return False, "Bölüm seçimi gereklidir.", None
        
        if not first_name or not first_name.strip():
            return False, "Ad gereklidir.", None
        
        if not last_name or not last_name.strip():
            return False, "Soyad gereklidir.", None
        
        if not title or not title.strip():
            return False, "Unvan gereklidir.", None
        
        if not email or not email.strip():
            email = generate_email(first_name.strip(), last_name.strip())
        
        existing = self.repository.get_by_email(email.strip())
        if existing:
            base_email = email.strip()
            counter = 1
            while existing:
                email = base_email.replace('@', f'{counter}@')
                counter += 1
                existing = self.repository.get_by_email(email)
        
        if available_days is None:
            available_days = DEFAULT_AVAILABLE_DAYS.copy()
        
        lecturer = Lecturer(
            department_id=department_id,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            title=title.strip(),
            email=email.strip(),
            available_days=available_days
        )
        
        try:
            lecturer_id = self.repository.create(lecturer)
            return True, "Öğretim görevlisi başarıyla oluşturuldu.", lecturer_id
        except Exception as e:
            return False, f"Öğretim görevlisi oluşturulamadı: {str(e)}", None
    
    def update(self, lecturer_id: int, department_id: int, first_name: str, last_name: str,
               title: str, email: str = None, available_days: List[str] = None) -> Tuple[bool, str]:
        lecturer = self.repository.get_by_id(lecturer_id)
        if not lecturer:
            return False, "Öğretim görevlisi bulunamadı."
        
        if not department_id:
            return False, "Bölüm seçimi gereklidir."
        
        if not first_name or not first_name.strip():
            return False, "Ad gereklidir."
        
        if not last_name or not last_name.strip():
            return False, "Soyad gereklidir."
        
        if not title or not title.strip():
            return False, "Unvan gereklidir."
        
        if not email or not email.strip():
            email = generate_email(first_name.strip(), last_name.strip())
        
        existing = self.repository.get_by_email(email.strip())
        if existing and existing.id != lecturer_id:
            base_email = email.strip()
            counter = 1
            while existing and existing.id != lecturer_id:
                email = base_email.replace('@', f'{counter}@')
                counter += 1
                existing = self.repository.get_by_email(email)
        
        lecturer.department_id = department_id
        lecturer.first_name = first_name.strip()
        lecturer.last_name = last_name.strip()
        lecturer.title = title.strip()
        lecturer.email = email.strip()
        
        if available_days is not None:
            lecturer.available_days = available_days
        
        if self.repository.update(lecturer):
            return True, "Öğretim görevlisi başarıyla güncellendi."
        return False, "Öğretim görevlisi güncellenemedi."
    
    def update_available_days(self, lecturer_id: int, available_days: List[str]) -> Tuple[bool, str]:
        lecturer = self.repository.get_by_id(lecturer_id)
        if not lecturer:
            return False, "Öğretim görevlisi bulunamadı."
        
        valid_days = [d for d in available_days if d in ALL_WEEKDAYS]
        
        if self.repository.update_available_days(lecturer_id, valid_days):
            return True, "Müsait günler başarıyla güncellendi."
        return False, "Müsait günler güncellenemedi."
    
    def delete(self, lecturer_id: int) -> Tuple[bool, str]:
        lecturer = self.repository.get_by_id(lecturer_id)
        if not lecturer:
            return False, "Öğretim görevlisi bulunamadı."
        
        if self.repository.delete(lecturer_id):
            return True, "Öğretim görevlisi başarıyla silindi."
        return False, "Öğretim görevlisi silinemedi."
    
    def search(self, keyword: str) -> List[Lecturer]:
        if not keyword or not keyword.strip():
            return self.get_all()
        return self.repository.search('last_name', keyword.strip())
    
    def get_count(self) -> int:
        return self.repository.count()
    
    def get_titles(self) -> List[str]:
        return [
            "Prof. Dr.",
            "Doç. Dr.",
            "Dr. Öğr. Üyesi",
            "Öğr. Gör. Dr.",
            "Öğr. Gör.",
            "Arş. Gör. Dr.",
            "Arş. Gör."
        ]
    
    def get_weekdays(self) -> List[str]:
        return ALL_WEEKDAYS.copy()
