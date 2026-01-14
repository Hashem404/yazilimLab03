"""
Temel repository sınıfı - CRUD operasyonları
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Any
from src.config.database import get_connection, release_connection

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    
    def __init__(self):
        self.table_name: str = ""
    
    @abstractmethod
    def _row_to_entity(self, row: tuple, columns: List[str]) -> T:
        pass
    
    @abstractmethod
    def _entity_to_values(self, entity: T) -> tuple:
        pass
    
    def _execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            cursor.close()
            return rows, columns
        except Exception as e:
            print(f"Sorgu hatası: {e}")
            raise
        finally:
            if conn:
                release_connection(conn)
    
    def _execute_non_query(self, query: str, params: tuple = None, return_id: bool = False) -> Optional[int]:
        """INSERT, UPDATE, DELETE sorgusu çalıştırır"""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            result = None
            if return_id:
                cursor.execute("SELECT LASTVAL()")
                result = cursor.fetchone()[0]
            
            conn.commit()
            cursor.close()
            return result
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Sorgu hatası: {e}")
            raise
        finally:
            if conn:
                release_connection(conn)
    
    def get_all(self) -> List[T]:
        query = f"SELECT * FROM {self.table_name}"
        rows, columns = self._execute_query(query)
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_id(self, id: int) -> Optional[T]:
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        rows, columns = self._execute_query(query, (id,))
        if rows:
            return self._row_to_entity(rows[0], columns)
        return None
    
    def delete(self, id: int) -> bool:
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        try:
            self._execute_non_query(query, (id,))
            return True
        except Exception:
            return False
    
    def count(self) -> int:
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        rows, _ = self._execute_query(query)
        return rows[0][0] if rows else 0
    
    def exists(self, id: int) -> bool:
        query = f"SELECT EXISTS(SELECT 1 FROM {self.table_name} WHERE id = %s)"
        rows, _ = self._execute_query(query, (id,))
        return rows[0][0] if rows else False
    
    def search(self, column: str, value: Any) -> List[T]:
        query = f"SELECT * FROM {self.table_name} WHERE {column} ILIKE %s"
        rows, columns = self._execute_query(query, (f"%{value}%",))
        return [self._row_to_entity(row, columns) for row in rows]
