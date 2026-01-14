"""
Kullanıcı repository sınıfı
"""

from typing import List, Optional
from datetime import datetime
from src.repositories.base_repository import BaseRepository
from src.models.user import User


class UserRepository(BaseRepository[User]):
    
    def __init__(self):
        super().__init__()
        self.table_name = "users"
    
    def _row_to_entity(self, row: tuple, columns: List[str]) -> User:
        data = dict(zip(columns, row))
        return User.from_dict(data)
    
    def _entity_to_values(self, entity: User) -> tuple:
        return (
            entity.username,
            entity.password_hash,
            entity.email,
            entity.first_name,
            entity.last_name,
            entity.role,
            entity.department_id,
            entity.is_active
        )
    
    def create(self, user: User) -> int:
        query = """
            INSERT INTO users (username, password_hash, email, first_name, last_name, role, department_id, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        values = self._entity_to_values(user)
        return self._execute_non_query(query, values, return_id=True)
    
    def update(self, user: User) -> bool:
        query = """
            UPDATE users
            SET username = %s, password_hash = %s, email = %s, first_name = %s,
                last_name = %s, role = %s, department_id = %s, is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        values = self._entity_to_values(user) + (user.id,)
        try:
            self._execute_non_query(query, values)
            return True
        except Exception:
            return False
    
    def get_by_username(self, username: str) -> Optional[User]:
        query = "SELECT * FROM users WHERE username = %s"
        rows, columns = self._execute_query(query, (username,))
        if rows:
            return self._row_to_entity(rows[0], columns)
        return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        query = "SELECT * FROM users WHERE email = %s"
        rows, columns = self._execute_query(query, (email,))
        if rows:
            return self._row_to_entity(rows[0], columns)
        return None
    
    def get_active_users(self) -> List[User]:
        query = "SELECT * FROM users WHERE is_active = TRUE ORDER BY username"
        rows, columns = self._execute_query(query)
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_role(self, role: str) -> List[User]:
        query = "SELECT * FROM users WHERE role = %s ORDER BY username"
        rows, columns = self._execute_query(query, (role,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def update_last_login(self, user_id: int) -> bool:
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s"
        try:
            self._execute_non_query(query, (user_id,))
            return True
        except Exception:
            return False
    
    def update_password(self, user_id: int, password_hash: str) -> bool:
        query = "UPDATE users SET password_hash = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        try:
            self._execute_non_query(query, (password_hash, user_id))
            return True
        except Exception:
            return False
    
    def deactivate(self, user_id: int) -> bool:
        query = "UPDATE users SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        try:
            self._execute_non_query(query, (user_id,))
            return True
        except Exception:
            return False
    
    def activate(self, user_id: int) -> bool:
        query = "UPDATE users SET is_active = TRUE, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        try:
            self._execute_non_query(query, (user_id,))
            return True
        except Exception:
            return False
    
    def username_exists(self, username: str, exclude_id: int = None) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE username = %s AND id != COALESCE(%s, -1))"
        rows, _ = self._execute_query(query, (username, exclude_id))
        return rows[0][0] if rows else False
    
    def email_exists(self, email: str, exclude_id: int = None) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE email = %s AND id != COALESCE(%s, -1))"
        rows, _ = self._execute_query(query, (email, exclude_id))
        return rows[0][0] if rows else False
    
    def authenticate(self, username: str, password_hash: str) -> Optional[User]:
        query = """
            SELECT * FROM users
            WHERE username = %s
            AND password_hash = %s
            AND is_active = TRUE
        """
        rows, columns = self._execute_query(query, (username, password_hash))
        
        if rows:
            user = self._row_to_entity(rows[0], columns)
            self.update_last_login(user.id)
            return user
        return None
