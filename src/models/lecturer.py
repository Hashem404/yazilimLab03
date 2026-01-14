"""
Öğretim görevlisi model sınıfı
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


DEFAULT_AVAILABLE_DAYS = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']

ALL_WEEKDAYS = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']


@dataclass
class Lecturer:
    """Öğretim görevlisi entity sınıfı"""
    
    id: Optional[int] = None
    department_id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    title: str = "" 
    email: Optional[str] = None
    available_days: List[str] = field(default_factory=lambda: DEFAULT_AVAILABLE_DAYS.copy())
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    department_name: Optional[str] = None
    faculty_name: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.available_days is None:
            self.available_days = DEFAULT_AVAILABLE_DAYS.copy()
    
    @property
    def full_name(self) -> str:
        return f"{self.title} {self.first_name} {self.last_name}".strip()
    
    @property
    def available_days_display(self) -> str:
        if not self.available_days:
            return "Belirlenmemiş"
        day_short = {
            'Pazartesi': 'Pzt',
            'Salı': 'Sal',
            'Çarşamba': 'Çar',
            'Perşembe': 'Per',
            'Cuma': 'Cum'
        }
        return ', '.join([day_short.get(d, d) for d in self.available_days])
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'department_id': self.department_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'title': self.title,
            'email': self.email,
            'available_days': self.available_days,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Lecturer':
        available_days = data.get('available_days')
        if available_days is None:
            available_days = DEFAULT_AVAILABLE_DAYS.copy()
        elif isinstance(available_days, str):
            available_days = [d.strip() for d in available_days.strip('{}').split(',') if d.strip()]
        elif isinstance(available_days, list):
            available_days = available_days.copy() if available_days else DEFAULT_AVAILABLE_DAYS.copy()
        
        return cls(
            id=data.get('id'),
            department_id=data.get('department_id'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            title=data.get('title', ''),
            email=data.get('email'),
            available_days=available_days,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            department_name=data.get('department_name'),
            faculty_name=data.get('faculty_name')
        )
    
    def is_available_on(self, day: str) -> bool:
        return day in self.available_days
    
    def get_unavailable_days(self) -> List[str]:
        return [d for d in ALL_WEEKDAYS if d not in self.available_days]
    
    def __str__(self) -> str:
        return self.full_name
