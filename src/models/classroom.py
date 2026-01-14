"""
Derslik model sınıfı
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


CLASSROOM_TYPES = [
    ('STANDART', 'Standart Derslik'),
    ('LAB', 'Laboratuvar'),
    ('OFIS', 'Ofis'),
    ('DEKANLIK', 'Dekanlık'),
    ('BILGISALONU', 'Bilgisayar Salonu'),
    ('KONFERANS', 'Konferans Salonu')
]

CLASSROOM_TYPE_MAP = {
    'STANDART': 'Standart Derslik',
    'LAB': 'Laboratuvar',
    'OFIS': 'Ofis',
    'DEKANLIK': 'Dekanlık',
    'BILGISALONU': 'Bilgisayar Salonu',
    'KONFERANS': 'Konferans Salonu'
}


@dataclass
class Classroom:
    """Derslik entity sınıfı"""
    
    id: Optional[int] = None
    name: str = ""
    faculty_id: Optional[int] = None
    capacity: int = 0
    has_computer: bool = False
    is_suitable: bool = True
    room_type: str = "STANDART"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    faculty_name: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'faculty_id': self.faculty_id,
            'capacity': self.capacity,
            'has_computer': self.has_computer,
            'is_suitable': self.is_suitable,
            'room_type': self.room_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'faculty_name': self.faculty_name
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Classroom':
        room_type_raw = data.get('room_type', 'STANDART')
        room_type = room_type_raw.upper()
        if room_type not in CLASSROOM_TYPE_MAP:
            room_type = 'STANDART'
        
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            faculty_id=data.get('faculty_id'),
            capacity=data.get('capacity', 0),
            has_computer=data.get('has_computer', False),
            is_suitable=data.get('is_suitable', True),
            room_type=room_type,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            faculty_name=data.get('faculty_name')
        )
    
    @property
    def room_type_display(self) -> str:
        return CLASSROOM_TYPE_MAP.get(self.room_type, self.room_type)
    
    def __str__(self) -> str:
        faculty_display = self.faculty_name if self.faculty_name else "Belirsiz"
        suitable_status = "✓" if self.is_suitable else "✗"
        type_display = self.room_type_display
        return f"{faculty_display} - {self.name} ({type_display}, Kapasite: {self.capacity}, Sınav Uygun: {suitable_status})"
