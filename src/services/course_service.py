"""
Ders servisi
"""

from typing import List, Optional, Tuple
from src.models.course import (
    Course, EXAM_DURATION_OPTIONS, REQUIRED_ROOM_TYPE_OPTIONS,
    REQUIRED_ROOM_TYPE_MAP, EXAM_TYPE_MAP, COURSE_TYPE_MAP
)
from src.repositories.course_repository import CourseRepository


class CourseService:
    def __init__(self):
        self.repository = CourseRepository()
    
    def get_all(self) -> List[Course]:
        return self.repository.get_all_with_details()
    
    def get_by_id(self, course_id: int) -> Optional[Course]:
        return self.repository.get_by_id(course_id)
    
    def get_by_code(self, code: str) -> Optional[Course]:
        return self.repository.get_by_code(code)
    
    def get_by_department_id(self, department_id: int) -> List[Course]:
        return self.repository.get_by_department_id(department_id)
    
    def get_by_lecturer_id(self, lecturer_id: int) -> List[Course]:
        return self.repository.get_by_lecturer_id(lecturer_id)
    
    def get_by_year_semester(self, year: int, semester: int) -> List[Course]:
        return self.repository.get_by_year_semester(year, semester)
    
    def get_exam_duration_options(self) -> List[tuple]:
        return EXAM_DURATION_OPTIONS
    
    def get_required_room_type_options(self) -> List[tuple]:
        return REQUIRED_ROOM_TYPE_OPTIONS
    
    def create(self, department_id: int, lecturer_id: int, code: str, name: str,
               credit: int, year: int = 1, semester: int = 1, student_count: int = 0,
               lecturer_count: int = 1, exam_type: str = "Yazılı", exam_duration: int = 60,
               has_exam: bool = True, period: int = None, theory_hours: int = 0,
               lab_hours: int = 0, course_type: str = "Zorunlu",
               description: str = None, required_room_type: str = "ANY") -> Tuple[bool, str, Optional[int]]:
        if not department_id:
            return False, "Bölüm seçimi gereklidir.", None
        
        if not code or not code.strip():
            return False, "Ders kodu gereklidir.", None
        
        if not name or not name.strip():
            return False, "Ders adı gereklidir.", None
        
        if credit < 0:
            return False, "Kredi sıfır veya pozitif olmalıdır.", None
        
        if period is not None:
            year = ((period - 1) // 2) + 1  # 1-2 -> 1, 3-4 -> 2, 5-6 -> 3, 7-8 -> 4
            semester = ((period - 1) % 2) + 1  # Tek dönemler -> 1, çift dönemler -> 2
        
        if year not in [1, 2, 3, 4]:
            year = 1 
        
        if semester not in [1, 2]:
            semester = 1
        
        if student_count < 0:
            student_count = 0
        
        if lecturer_count < 1:
            lecturer_count = 1
        
        normalized_course_type = COURSE_TYPE_MAP.get(course_type, course_type)
        if course_type == 'Proje' or normalized_course_type == 'Proje':
            has_exam = False
        
        if not has_exam:
            exam_duration = 0
            exam_type = ""
        
        valid_durations = [d[0] for d in EXAM_DURATION_OPTIONS]
        if has_exam and exam_duration not in valid_durations:
            exam_duration = 60
        
        normalized_room_type = required_room_type.upper()
        if normalized_room_type not in REQUIRED_ROOM_TYPE_MAP:
            normalized_room_type = "ANY"
    
        existing = self.repository.get_by_code(code.strip().upper())
        if existing:
            return False, "Bu ders kodu zaten kullanılıyor.", None
        
        course = Course(
            department_id=department_id,
            lecturer_id=lecturer_id if lecturer_id else None,
            code=code.strip().upper(),
            name=name.strip(),
            credit=credit,
            year=year,
            semester=semester,
            period=period if period else semester,
            theory_hours=theory_hours,
            lab_hours=lab_hours,
            course_type=normalized_course_type,
            description=description,
            student_count=student_count,
            lecturer_count=lecturer_count,
            exam_type=exam_type,
            exam_duration=exam_duration,
            has_exam=has_exam,
            required_room_type=normalized_room_type
        )
        
        try:
            course_id = self.repository.create(course)
            return True, "Ders başarıyla oluşturuldu.", course_id
        except Exception as e:
            return False, f"Ders oluşturulamadı: {str(e)}", None
    
    def update(self, course_id: int, department_id: int, lecturer_id: int, code: str,
               name: str, credit: int, year: int = 1, semester: int = 1, student_count: int = 0,
               lecturer_count: int = 1, exam_type: str = "Yazılı", exam_duration: int = 60,
               has_exam: bool = True, period: int = None, theory_hours: int = 0,
               lab_hours: int = 0, course_type: str = "Zorunlu",
               description: str = None, required_room_type: str = "ANY") -> Tuple[bool, str]:
        course = self.repository.get_by_id(course_id)
        if not course:
            return False, "Ders bulunamadı."
        
        if not department_id:
            return False, "Bölüm seçimi gereklidir."
        
        if not code or not code.strip():
            return False, "Ders kodu gereklidir."
        
        if not name or not name.strip():
            return False, "Ders adı gereklidir."
        
        if period is not None:
            year = ((period - 1) // 2) + 1  # 1-2 -> 1, 3-4 -> 2, 5-6 -> 3, 7-8 -> 4
            semester = ((period - 1) % 2) + 1  # Tek dönemler -> 1, çift dönemler -> 2
        
        if year not in [1, 2, 3, 4]:
            year = 1
        
        if semester not in [1, 2]:
            semester = 1
        
        if lecturer_count < 1:
            lecturer_count = 1
        
        normalized_course_type = COURSE_TYPE_MAP.get(course_type, course_type)
        if course_type == 'Proje' or normalized_course_type == 'Proje':
            has_exam = False
        
        if not has_exam:
            exam_duration = 0
            exam_type = ""
        
        valid_durations = [d[0] for d in EXAM_DURATION_OPTIONS]
        if has_exam and exam_duration not in valid_durations:
            exam_duration = 60
        
        normalized_room_type = required_room_type.upper()
        if normalized_room_type not in REQUIRED_ROOM_TYPE_MAP:
            normalized_room_type = "ANY"
        
        existing = self.repository.get_by_code(code.strip().upper())
        if existing and existing.id != course_id:
            return False, "Bu ders kodu zaten kullanılıyor."
        
        course.department_id = department_id
        course.lecturer_id = lecturer_id if lecturer_id else None
        course.code = code.strip().upper()
        course.name = name.strip()
        course.credit = credit
        course.year = year
        course.semester = semester
        course.period = period if period else semester
        course.theory_hours = theory_hours
        course.lab_hours = lab_hours
        course.course_type = normalized_course_type
        course.description = description
        course.student_count = student_count if student_count >= 0 else 0
        course.lecturer_count = lecturer_count
        course.exam_type = exam_type
        course.exam_duration = exam_duration
        course.has_exam = has_exam
        course.required_room_type = normalized_room_type
        
        if self.repository.update(course):
            return True, "Ders başarıyla güncellendi."
        return False, "Ders güncellenemedi."
    
    def delete(self, course_id: int) -> Tuple[bool, str]:
        course = self.repository.get_by_id(course_id)
        if not course:
            return False, "Ders bulunamadı."
        
        if self.repository.delete(course_id):
            return True, "Ders başarıyla silindi."
        return False, "Ders silinemedi."
    
    def search(self, keyword: str) -> List[Course]:
        if not keyword or not keyword.strip():
            return self.get_all()
        return self.repository.search('name', keyword.strip())
    
    def get_count(self) -> int:
        return self.repository.count()
