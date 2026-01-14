"""
Öğrenci model sınıfı
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Student:
    
    id: Optional[int] = None
    student_number: str = ""
    first_name: str = ""
    last_name: str = ""
    email: Optional[str] = None
    department_id: Optional[int] = None
    year: int = 1
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    department_name: Optional[str] = None
    faculty_name: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'student_number': self.student_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'department_id': self.department_id,
            'year': self.year,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Student':
        return cls(
            id=data.get('id'),
            student_number=data.get('student_number', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            email=data.get('email'),
            department_id=data.get('department_id'),
            year=data.get('year', 1),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            department_name=data.get('department_name'),
            faculty_name=data.get('faculty_name')
        )
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    def __str__(self) -> str:
        dept_info = self.department_name if self.department_name else f"Bölüm ID: {self.department_id}"
        return f"{self.student_number} - {self.full_name} ({dept_info}, {self.year}. Sınıf)"


@dataclass
class StudentCourse:
    
    id: Optional[int] = None
    student_id: Optional[int] = None
    course_id: Optional[int] = None
    semester: Optional[str] = None  # Örn: "2023-2024 Güz"
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    # Join sonucu eklenen alanlar
    student_number: Optional[str] = None
    student_name: Optional[str] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    department_id: Optional[int] = None
    course_year: Optional[int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'semester': self.semester,
            'is_active': self.is_active,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StudentCourse':
        return cls(
            id=data.get('id'),
            student_id=data.get('student_id'),
            course_id=data.get('course_id'),
            semester=data.get('semester'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            student_number=data.get('student_number'),
            student_name=data.get('student_name'),
            course_code=data.get('course_code'),
            course_name=data.get('course_name'),
            department_id=data.get('department_id'),
            course_year=data.get('course_year')
        )
    
    def __str__(self) -> str:
        student_info = self.student_number if self.student_number else f"Öğrenci ID: {self.student_id}"
        course_info = self.course_code if self.course_code else f"Ders ID: {self.course_id}"
        return f"{student_info} -> {course_info}"
