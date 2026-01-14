"""
Ders model sınıfı
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


COURSE_TYPES = [
    ('Zorunlu', 'Zorunlu'),
    ('Alan Seçmeli', 'Alan Seçmeli'),
    ('Üniversite Seçmeli', 'Üniversite Seçmeli'),
    ('Proje', 'Proje')
]

COURSE_TYPE_MAP = {
    'Zorunlu': 'Zorunlu',
    'Alan Seçmeli': 'Alan Seçmeli',
    'Üniversite Seçmeli': 'Üniversite Seçmeli',
    'Proje': 'Proje',
    'mandatory': 'Zorunlu',
    'elective': 'Alan Seçmeli',
    'technical_elective': 'Alan Seçmeli',
    'non_technical_elective': 'Üniversite Seçmeli'
}

EXAM_TYPES = [
    ('Yazılı', 'Yazılı'),
    ('Test', 'Test'),
    ('Uygulama', 'Uygulama'),
    ('Sözlü', 'Sözlü'),
    ('Proje', 'Proje'),
    ('Ödev', 'Ödev')
]

EXAM_TYPE_MAP = {
    'Yazılı': 'Yazılı',
    'Test': 'Test',
    'Uygulama': 'Uygulama',
    'Sözlü': 'Sözlü',
    'Proje': 'Proje',
    'Ödev': 'Ödev'
}

EXAM_DURATION_OPTIONS = [
    (30, '30 dakika'),
    (60, '60 dakika'),
    (90, '90 dakika'),
    (120, '120 dakika'),
    (240, '4 saat'),
    (360, '6 saat'),
    (480, '8 saat')
]

REQUIRED_ROOM_TYPE_OPTIONS = [
    ('STANDART', 'Standart Derslik'),
    ('LAB', 'Laboratuvar'),
    ('OFIS', 'Ofis'),
    ('DEKANLIK', 'Dekanlık'),
    ('BILGISALONU', 'Bilgisayar Salonu'),
    ('KONFERANS', 'Konferans Salonu'),
    ('ANY', 'Herhangi Bir')
]

REQUIRED_ROOM_TYPE_MAP = {
    'STANDART': 'Standart Derslik',
    'LAB': 'Laboratuvar',
    'OFIS': 'Ofis',
    'DEKANLIK': 'Dekanlık',
    'BILGISALONU': 'Bilgisayar Salonu',
    'KONFERANS': 'Konferans Salonu',
    'ANY': 'Herhangi Bir'
}


@dataclass
class Course:
    
    id: Optional[int] = None
    department_id: Optional[int] = None
    lecturer_id: Optional[int] = None
    code: str = ""
    name: str = ""
    credit: int = 3
    year: int = 1
    semester: int = 1
    period: Optional[int] = None
    theory_hours: int = 0
    lab_hours: int = 0
    course_type: str = "Zorunlu"
    description: Optional[str] = None
    student_count: int = 0
    lecturer_count: int = 1
    exam_type: str = "Yazılı"
    exam_duration: int = 60
    has_exam: bool = True
    required_room_type: str = "ANY"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    department_name: Optional[str] = None
    lecturer_name: Optional[str] = None
    faculty_name: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.period is None:
            self.period = self.semester
        elif self.semester == 1 and self.period != 1:
            self.semester = self.period
        if not self.has_exam:
            self.exam_duration = 0
            self.exam_type = ""

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'department_id': self.department_id,
            'lecturer_id': self.lecturer_id,
            'code': self.code,
            'name': self.name,
            'credit': self.credit,
            'year': self.year,
            'semester': self.semester,
            'period': self.period,
            'theory_hours': self.theory_hours,
            'lab_hours': self.lab_hours,
            'course_type': self.course_type,
            'description': self.description,
            'student_count': self.student_count,
            'lecturer_count': self.lecturer_count,
            'exam_type': self.exam_type,
            'exam_duration': self.exam_duration,
            'has_exam': self.has_exam,
            'required_room_type': self.required_room_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Course':
        semester_val = data.get('semester', 1)
        period_val = data.get('period')
        if period_val is None:
            period_val = semester_val
        
        course_type_raw = data.get('course_type', 'Zorunlu')
        course_type = COURSE_TYPE_MAP.get(course_type_raw, course_type_raw)
        
        has_exam = data.get('has_exam')
        if has_exam is None:
            has_exam = course_type != 'Proje'
        
        exam_type_raw = data.get('exam_type', 'Yazılı')
        exam_type = EXAM_TYPE_MAP.get(exam_type_raw, exam_type_raw) if exam_type_raw else 'Yazılı'
        
        exam_duration = data.get('exam_duration', 60)
        if not has_exam:
            exam_duration = 0
            exam_type = ""
        
        required_room_type_raw = data.get('required_room_type', 'ANY')
        required_room_type = required_room_type_raw.upper()
        if required_room_type not in REQUIRED_ROOM_TYPE_MAP:
            required_room_type = 'ANY'
        
        return cls(
            id=data.get('id'),
            department_id=data.get('department_id'),
            lecturer_id=data.get('lecturer_id'),
            code=data.get('code', ''),
            name=data.get('name', ''),
            credit=data.get('credit', 3),
            year=data.get('year', 1),
            semester=semester_val,
            period=period_val,
            theory_hours=data.get('theory_hours', 0),
            lab_hours=data.get('lab_hours', 0),
            course_type=course_type,
            description=data.get('description'),
            student_count=data.get('student_count', 0),
            lecturer_count=data.get('lecturer_count', 1),
            exam_type=exam_type,
            exam_duration=exam_duration,
            has_exam=has_exam,
            required_room_type=required_room_type,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            department_name=data.get('department_name'),
            lecturer_name=data.get('lecturer_name'),
            faculty_name=data.get('faculty_name')
        )

    @property
    def course_type_display(self) -> str:
        return COURSE_TYPE_MAP.get(self.course_type, self.course_type)
    
    @property
    def has_exam_display(self) -> str:
        return "Evet" if self.has_exam else "Hayır"
    
    @property
    def exam_type_display(self) -> str:
        if not self.has_exam:
            return "-"
        return EXAM_TYPE_MAP.get(self.exam_type, self.exam_type)
    
    @property
    def exam_duration_display(self) -> str:
        if not self.has_exam or self.exam_duration == 0:
            return "-"
        return f"{self.exam_duration} dk"
    
    @property
    def required_room_type_display(self) -> str:
        return REQUIRED_ROOM_TYPE_MAP.get(self.required_room_type, self.required_room_type)

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
