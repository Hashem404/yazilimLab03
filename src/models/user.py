"""
Kullanıcı model sınıfı
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import hashlib


@dataclass
class User:
    
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    email: Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    role: str = "viewer"
    department_id: Optional[int] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    def set_password(self, password: str):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'department_id': self.department_id,
            'is_active': self.is_active,
            'last_login': self.last_login,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(
            id=data.get('id'),
            username=data.get('username', ''),
            password_hash=data.get('password_hash', ''),
            email=data.get('email'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=data.get('role', 'viewer'),
            department_id=data.get('department_id'),
            is_active=data.get('is_active', True),
            last_login=data.get('last_login'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
    
    def has_permission(self, permission: str) -> bool:
        permissions = {
            'admin': ['create', 'read', 'update', 'delete', 'export', 'manage_users', 'manage_all'],
            'bolum_yetkilisi': ['create', 'read', 'update', 'delete', 'export', 'manage_department'],
            'hoca': ['read', 'view_schedule'],
            'ogrenci': ['read', 'view_schedule']
        }
        return permission in permissions.get(self.role, [])
    
    def is_admin(self) -> bool:
        return self.role == 'admin'
    
    def is_bolum_yetkilisi(self) -> bool:
        return self.role == 'bolum_yetkilisi'
    
    def is_hoca(self) -> bool:
        return self.role == 'hoca'
    
    def is_ogrenci(self) -> bool:
        return self.role == 'ogrenci'
    
    def can_manage_department(self, department_id: int) -> bool:
        if self.is_admin():
            return True
        if self.is_bolum_yetkilisi() and self.department_id == department_id:
            return True
        return False
