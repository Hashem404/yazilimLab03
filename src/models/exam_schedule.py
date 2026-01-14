"""
Sınav programı model sınıfı
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, date, time


@dataclass
class ExamSchedule:
    
    id: Optional[int] = None
    course_id: Optional[int] = None
    classroom_id: Optional[int] = None
    exam_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    exam_type: str = "final"  
    status: str = "planned" 
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    classroom_name: Optional[str] = None
    faculty_name: Optional[str] = None
    lecturer_name: Optional[str] = None
    department_name: Optional[str] = None
    student_count: Optional[int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'course_id': self.course_id,
            'classroom_id': self.classroom_id,
            'exam_date': self.exam_date,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'exam_type': self.exam_type,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ExamSchedule':
        return cls(
            id=data.get('id'),
            course_id=data.get('course_id'),
            classroom_id=data.get('classroom_id'),
            exam_date=data.get('exam_date'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            exam_type=data.get('exam_type', 'final'),
            status=data.get('status', 'planned'),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            course_code=data.get('course_code'),
            course_name=data.get('course_name'),
            classroom_name=data.get('classroom_name'),
            faculty_name=data.get('faculty_name'),
            lecturer_name=data.get('lecturer_name'),
            department_name=data.get('department_name'),
            student_count=data.get('student_count')
        )
    
    def __str__(self) -> str:
        return f"{self.course_code} - {self.exam_date} {self.start_time}"


@dataclass
class ExamSupervisor:
    
    id: Optional[int] = None
    exam_schedule_id: Optional[int] = None
    lecturer_id: Optional[int] = None
    is_chief: bool = False  # Baş gözetmen mi?
    created_at: Optional[datetime] = None
    
    lecturer_name: Optional[str] = None
