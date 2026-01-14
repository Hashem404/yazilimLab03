"""
Kimlik doğrulama controller
View ile Service arasında köprü görevi görür
"""

from typing import Callable, Optional, Any
from src.services.auth_service import AuthService


class AuthController:
    
    def __init__(self, view: Any = None):
        self.auth_service = AuthService()
        self.view = view
        self.current_user: Optional[dict] = None
        self._on_login_success: Optional[Callable] = None
        self._on_logout: Optional[Callable] = None
    
    def set_login_callback(self, callback: Callable) -> None:
        self._on_login_success = callback
    
    def set_logout_callback(self, callback: Callable) -> None:
        self._on_logout = callback
    
    def login(self, username: str, password: str) -> dict:
        if not username or not password:
            return {
                'success': False,
                'message': 'Kullanıcı adı ve şifre gerekli',
                'user': None
            }
        
        success, message = self.auth_service.login(username, password)
        
        if success:
            user_info = self.auth_service.get_user_info()
            self.current_user = user_info
            
            if self._on_login_success:
                self._on_login_success(user_info)
            
            return {
                'success': True,
                'message': 'Giriş başarılı',
                'user': user_info
            }
        
        return {
            'success': False,
            'message': message or 'Kullanıcı adı veya şifre hatalı',
            'user': None
        }
    
    def logout(self) -> dict:
        self.auth_service.logout()
        self.current_user = None
        
        if self._on_logout:
            self._on_logout()
        
        return {'success': True, 'message': 'Çıkış yapıldı'}
    
    def is_authenticated(self) -> bool:
        return self.current_user is not None
    
    def has_permission(self, permission: str) -> bool:
        return self.auth_service.has_permission(permission)
    
    def has_role(self, role: str) -> bool:
        if not self.current_user:
            return False
        return self.current_user.get('role') == role
    
    def get_current_user(self) -> Optional[dict]:
        return self.current_user
    
    def get_current_user_role(self) -> Optional[str]:
        if self.current_user:
            return self.current_user.get('role')
        return None
    
    def change_password(self, old_password: str, new_password: str) -> dict:
        success, message = self.auth_service.change_password(old_password, new_password)
        return {'success': success, 'message': message}
    
    def can_create(self) -> bool:
        return self.has_permission('create')
    
    def can_edit(self) -> bool:
        return self.has_permission('update')
    
    def can_delete(self) -> bool:
        return self.has_permission('delete')
    
    def can_export(self) -> bool:
        return self.has_permission('export')
    
    def is_admin(self) -> bool:
        return self.has_role('admin')
    
    def is_bolum_yetkilisi(self) -> bool:
        return self.has_role('bolum_yetkilisi')
    
    def is_hoca(self) -> bool:
        return self.has_role('hoca')
    
    def is_ogrenci(self) -> bool:
        return self.has_role('ogrenci')
    
    def get_user_department_id(self) -> int:
        if self.current_user:
            return self.current_user.get('department_id')
        return None
