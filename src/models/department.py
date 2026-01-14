"""
Bölüm model sınıfı
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Department:
    
    id: Optional[int] = None
    faculty_id: Optional[int] = None
    name: str = ""
    code: str = ""
    head_name: Optional[str] = None
    head_of_department: Optional[str] = None 
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    faculty_name: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.head_of_department and not self.head_name:
            self.head_name = self.head_of_department
        elif self.head_name and not self.head_of_department:
            self.head_of_department = self.head_name
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'faculty_id': self.faculty_id,
            'name': self.name,
            'code': self.code,
            'head_name': self.head_name,
            'head_of_department': self.head_of_department,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Department':
        head = data.get('head_name') or data.get('head_of_department')
        return cls(
            id=data.get('id'),
            faculty_id=data.get('faculty_id'),
            name=data.get('name', ''),
            code=data.get('code', ''),
            head_name=head,
            head_of_department=head,
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            faculty_name=data.get('faculty_name')
        )
    
    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
