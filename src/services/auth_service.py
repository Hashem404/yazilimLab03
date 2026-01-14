"""
Kimlik doğrulama servisi
"""

from typing import Optional, Tuple
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.repositories.student_repository import StudentRepository
from src.repositories.lecturer_repository import LecturerRepository


class AuthService:
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.student_repository = StudentRepository()
        self.lecturer_repository = LecturerRepository()
        self._current_user: Optional[User] = None
    
    @property
    def current_user(self) -> Optional[User]:
        return self._current_user
    
    @property
    def is_authenticated(self) -> bool:
        return self._current_user is not None
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:

        if not username or not password:
            return False, "Kullanıcı adı ve şifre gereklidir."
        
        user = self.user_repository.get_by_username(username)
        
        if user is None:
            return False, "Kullanıcı bulunamadı."
        
        if not user.is_active:
            return False, "Bu hesap devre dışı bırakılmıştır."
        
        if not user.check_password(password):
            return False, "Şifre hatalı."
        
        self._current_user = user
        self.user_repository.update_last_login(user.id)
        
        return True, f"Hoş geldiniz, {user.full_name}!"
    
    def logout(self):
        self._current_user = None
    
    def has_permission(self, permission: str) -> bool:
        if self._current_user is None:
            return False
        return self._current_user.has_permission(permission)
    
    def change_password(self, old_password: str, new_password: str) -> Tuple[bool, str]:

        if self._current_user is None:
            return False, "Oturum açmanız gerekiyor."
        
        if not self._current_user.check_password(old_password):
            return False, "Mevcut şifre hatalı."
        
        if len(new_password) < 6:
            return False, "Yeni şifre en az 6 karakter olmalıdır."
        
        import hashlib
        new_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        if self.user_repository.update_password(self._current_user.id, new_hash):
            self._current_user.password_hash = new_hash
            return True, "Şifre başarıyla değiştirildi."
        
        return False, "Şifre değiştirilemedi."
    
    def register_user(self, username: str, password: str, email: str, 
                      first_name: str, last_name: str, role: str = "viewer") -> Tuple[bool, str]:

        if not self.has_permission('manage_users'):
            return False, "Bu işlem için yetkiniz yok."
        
        if self.user_repository.username_exists(username):
            return False, "Bu kullanıcı adı zaten kullanılıyor."
        
        if email and self.user_repository.email_exists(email):
            return False, "Bu e-posta adresi zaten kullanılıyor."
        
        if len(password) < 6:
            return False, "Şifre en az 6 karakter olmalıdır."
        
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)
        
        try:
            user_id = self.user_repository.create(user)
            return True, f"Kullanıcı başarıyla oluşturuldu. ID: {user_id}"
        except Exception as e:
            return False, f"Kullanıcı oluşturulamadı: {str(e)}"
    
    def get_user_info(self) -> Optional[dict]:
        """
        Mevcut kullanıcı bilgilerini döndürür.
        Role göre ek bilgiler (student_id, lecturer_id, student_number) ekler.
        """
        if self._current_user is None:
            return None
        
        user_info = {
            'id': self._current_user.id,
            'username': self._current_user.username,
            'full_name': self._current_user.full_name,
            'email': self._current_user.email,
            'role': self._current_user.role,
            'department_id': self._current_user.department_id
        }
        
        if self._current_user.is_ogrenci():
            student = self._find_student_by_user()
            if student:
                user_info['student_id'] = student.id
                user_info['student_number'] = student.student_number
        
        elif self._current_user.is_hoca():
            lecturer = self._find_lecturer_by_user()
            if lecturer:
                user_info['lecturer_id'] = lecturer.id
        
        return user_info
    
    def _find_student_by_user(self) -> Optional:
        from src.models.student import Student
        
        if self._current_user.email:
            student = self.student_repository.get_by_email(self._current_user.email)
            if student:
                return student
        
        if self._current_user.username:
            student = self.student_repository.get_by_student_number(self._current_user.username)
            if student:
                return student
        
        return None
    
    def _find_lecturer_by_user(self) -> Optional:
        from src.models.lecturer import Lecturer
        
        if self._current_user.email:
            lecturer = self.lecturer_repository.get_by_email(self._current_user.email)
            if lecturer:
                return lecturer
        
        if self._current_user.department_id:
            lecturers = self.lecturer_repository.get_by_department_id(self._current_user.department_id)
            for lecturer in lecturers:
                if (lecturer.first_name.lower() == self._current_user.first_name.lower() and
                    lecturer.last_name.lower() == self._current_user.last_name.lower()):
                    return lecturer
        
        return None
    
    def get_user_department_id(self) -> Optional[int]:
        if self._current_user is None:
            return None
        return self._current_user.department_id
    
    def is_admin(self) -> bool:
        if self._current_user is None:
            return False
        return self._current_user.is_admin()
    
    def is_bolum_yetkilisi(self) -> bool:
        if self._current_user is None:
            return False
        return self._current_user.is_bolum_yetkilisi()
    
    def is_hoca(self) -> bool:
        if self._current_user is None:
            return False
        return self._current_user.is_hoca()
    
    def is_ogrenci(self) -> bool:
        if self._current_user is None:
            return False
        return self._current_user.is_ogrenci()
