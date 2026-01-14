"""
Öğrenci ve Öğrenci-Ders repository sınıfları
"""

from typing import List, Optional, Set
from src.repositories.base_repository import BaseRepository
from src.models.student import Student, StudentCourse


class StudentRepository(BaseRepository[Student]):
    
    def __init__(self):
        super().__init__()
        self.table_name = "students"
    
    def _row_to_entity(self, row: tuple, columns: List[str]) -> Student:
        data = dict(zip(columns, row))
        return Student.from_dict(data)
    
    def _entity_to_values(self, entity: Student) -> tuple:
        return (
            entity.student_number,
            entity.first_name,
            entity.last_name,
            entity.email,
            entity.department_id,
            entity.year,
            entity.is_active
        )
    
    def create(self, student: Student) -> int:
        query = """
            INSERT INTO students (student_number, first_name, last_name, email, department_id, year, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (student_number) DO UPDATE
            SET first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                email = EXCLUDED.email,
                department_id = EXCLUDED.department_id,
                year = EXCLUDED.year,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """
        values = self._entity_to_values(student)
        return self._execute_non_query(query, values, return_id=True)
    
    def create_batch(self, students: List[Student]) -> int:
        """Toplu öğrenci kaydı için optimize edilmiş metot"""
        if not students:
            return 0
        
        query = """
            INSERT INTO students (student_number, first_name, last_name, email, department_id, year, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (student_number) DO UPDATE
            SET first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                email = EXCLUDED.email,
                department_id = EXCLUDED.department_id,
                year = EXCLUDED.year,
                updated_at = CURRENT_TIMESTAMP
        """
        
        values_list = [self._entity_to_values(s) for s in students]
        return self._execute_batch_non_query(query, values_list)
    
    def update(self, student: Student) -> bool:
        query = """
            UPDATE students
            SET student_number = %s, first_name = %s, last_name = %s, email = %s,
                department_id = %s, year = %s, is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        values = self._entity_to_values(student) + (student.id,)
        try:
            self._execute_non_query(query, values)
            return True
        except Exception:
            return False
    
    def get_by_student_number(self, student_number: str) -> Optional[Student]:
        query = """
            SELECT s.*, d.name as department_name, f.name as faculty_name
            FROM students s
            LEFT JOIN departments d ON s.department_id = d.id
            LEFT JOIN faculties f ON d.faculty_id = f.id
            WHERE s.student_number = %s
        """
        rows, columns = self._execute_query(query, (student_number,))
        if rows:
            return self._row_to_entity(rows[0], columns)
        return None
    
    def get_by_email(self, email: str) -> Optional[Student]:
        query = """
            SELECT s.*, d.name as department_name, f.name as faculty_name
            FROM students s
            LEFT JOIN departments d ON s.department_id = d.id
            LEFT JOIN faculties f ON d.faculty_id = f.id
            WHERE s.email = %s
        """
        rows, columns = self._execute_query(query, (email,))
        if rows:
            return self._row_to_entity(rows[0], columns)
        return None
    
    def get_by_department_id(self, department_id: int) -> List[Student]:
        query = """
            SELECT s.*, d.name as department_name, f.name as faculty_name
            FROM students s
            LEFT JOIN departments d ON s.department_id = d.id
            LEFT JOIN faculties f ON d.faculty_id = f.id
            WHERE s.department_id = %s AND s.is_active = TRUE
            ORDER BY s.student_number
        """
        rows, columns = self._execute_query(query, (department_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_all_with_details(self) -> List[Student]:
        query = """
            SELECT s.*, d.name as department_name, f.name as faculty_name
            FROM students s
            LEFT JOIN departments d ON s.department_id = d.id
            LEFT JOIN faculties f ON d.faculty_id = f.id
            WHERE s.is_active = TRUE
            ORDER BY d.name, s.year, s.student_number
        """
        rows, columns = self._execute_query(query)
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_student_numbers_by_course(self, course_id: int) -> Set[str]:
        """
        Belirli bir dersi alan tüm öğrencilerin numaralarını döndürür.
        Öğrenci bazlı çakışma kontrolü için kullanılır.
        """
        query = """
            SELECT s.student_number
            FROM student_courses sc
            INNER JOIN students s ON sc.student_id = s.id
            WHERE sc.course_id = %s AND sc.is_active = TRUE AND s.is_active = TRUE
        """
        rows, _ = self._execute_query(query, (course_id,))
        return {row[0] for row in rows if row[0]}
    
    def get_student_numbers_by_courses(self, course_ids: List[int]) -> dict:
        """
        Birden fazla ders için öğrenci numaralarını döndürür.
        
        Returns:
            dict: {course_id: set_of_student_numbers}
        """
        if not course_ids:
            return {}
        
        query = """
            SELECT sc.course_id, s.student_number
            FROM student_courses sc
            INNER JOIN students s ON sc.student_id = s.id
            WHERE sc.course_id = ANY(%s) AND sc.is_active = TRUE AND s.is_active = TRUE
        """
        rows, _ = self._execute_query(query, (course_ids,))
        
        result = {}
        for course_id in course_ids:
            result[course_id] = set()
        
        for course_id, student_number in rows:
            if course_id in result:
                result[course_id].add(student_number)
        
        return result
    
    def delete_by_department(self, department_id: int) -> int:
        """Belirli bir bölümden tüm öğrencileri siler (soft delete)"""
        query = "UPDATE students SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP WHERE department_id = %s"
        return self._execute_non_query(query, (department_id,))


class StudentCourseRepository(BaseRepository[StudentCourse]):
    
    def __init__(self):
        super().__init__()
        self.table_name = "student_courses"
    
    def _row_to_entity(self, row: tuple, columns: List[str]) -> StudentCourse:
        data = dict(zip(columns, row))
        return StudentCourse.from_dict(data)
    
    def _entity_to_values(self, entity: StudentCourse) -> tuple:
        return (
            entity.student_id,
            entity.course_id,
            entity.semester,
            entity.is_active
        )
    
    def create(self, student_course: StudentCourse) -> int:
        query = """
            INSERT INTO student_courses (student_id, course_id, semester, is_active)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (student_id, course_id) DO UPDATE
            SET semester = EXCLUDED.semester,
                is_active = EXCLUDED.is_active
            RETURNING id
        """
        values = self._entity_to_values(student_course)
        return self._execute_non_query(query, values, return_id=True)
    
    def create_batch(self, student_courses: List[StudentCourse]) -> int:
        """Toplu öğrenci-ders ilişkisi kaydı için optimize edilmiş metot"""
        if not student_courses:
            return 0
        
        query = """
            INSERT INTO student_courses (student_id, course_id, semester, is_active)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (student_id, course_id) DO UPDATE
            SET semester = EXCLUDED.semester,
                is_active = EXCLUDED.is_active
        """
        
        values_list = [self._entity_to_values(sc) for sc in student_courses]
        return self._execute_batch_non_query(query, values_list)
    
    def get_by_student_id(self, student_id: int) -> List[StudentCourse]:
        query = """
            SELECT sc.*, s.student_number, 
                   CONCAT(s.first_name, ' ', s.last_name) as student_name,
                   c.code as course_code, c.name as course_name,
                   c.department_id, c.year as course_year
            FROM student_courses sc
            INNER JOIN students s ON sc.student_id = s.id
            INNER JOIN courses c ON sc.course_id = c.id
            WHERE sc.student_id = %s AND sc.is_active = TRUE
            ORDER BY c.code
        """
        rows, columns = self._execute_query(query, (student_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_by_course_id(self, course_id: int) -> List[StudentCourse]:
        query = """
            SELECT sc.*, s.student_number, 
                   CONCAT(s.first_name, ' ', s.last_name) as student_name,
                   c.code as course_code, c.name as course_name,
                   c.department_id, c.year as course_year
            FROM student_courses sc
            INNER JOIN students s ON sc.student_id = s.id
            INNER JOIN courses c ON sc.course_id = c.id
            WHERE sc.course_id = %s AND sc.is_active = TRUE
            ORDER BY s.student_number
        """
        rows, columns = self._execute_query(query, (course_id,))
        return [self._row_to_entity(row, columns) for row in rows]
    
    def get_student_ids_by_course(self, course_id: int) -> Set[int]:
        """
        Belirli bir dersi alan tüm öğrenci ID'lerini döndürür.
        """
        query = """
            SELECT student_id
            FROM student_courses
            WHERE course_id = %s AND is_active = TRUE
        """
        rows, _ = self._execute_query(query, (course_id,))
        return {row[0] for row in rows}
    
    def get_student_ids_by_courses(self, course_ids: List[int]) -> dict:
        """
        Birden fazla ders için öğrenci ID'lerini döndürür.
        
        Returns:
            dict: {course_id: set_of_student_ids}
        """
        if not course_ids:
            return {}
        
        query = """
            SELECT course_id, student_id
            FROM student_courses
            WHERE course_id = ANY(%s) AND is_active = TRUE
        """
        rows, _ = self._execute_query(query, (course_ids,))
        
        result = {}
        for course_id in course_ids:
            result[course_id] = set()
        
        for course_id, student_id in rows:
            if course_id in result:
                result[course_id].add(student_id)
        
        return result
    
    def check_student_overlap(self, course_id1: int, course_id2: int) -> int:
        """
        İki ders arasında kaç öğrencinin çakıştığını döndürür.
        
        Args:
            course_id1: İlk dersin ID'si
            course_id2: İkinci dersin ID'si
            
        Returns:
            int: Çakışan öğrenci sayısı
        """
        query = """
            SELECT COUNT(DISTINCT sc1.student_id)
            FROM student_courses sc1
            INNER JOIN student_courses sc2 ON sc1.student_id = sc2.student_id
            WHERE sc1.course_id = %s 
              AND sc2.course_id = %s
              AND sc1.is_active = TRUE 
              AND sc2.is_active = TRUE
        """
        rows, _ = self._execute_query(query, (course_id1, course_id2))
        return rows[0][0] if rows else 0
    
    def get_conflicting_courses(self, course_id: int, min_overlap: int = 1) -> List[dict]:
        """
        Belirli bir dersle çakışan dersleri döndürür.
        
        Args:
            course_id: Ders ID'si
            min_overlap: Minimum çakışma sayısı
            
        Returns:
            List[dict]: [{course_id, course_code, course_name, overlap_count}]
        """
        query = """
            SELECT sc2.course_id, c.code as course_code, c.name as course_name,
                   COUNT(DISTINCT sc1.student_id) as overlap_count
            FROM student_courses sc1
            INNER JOIN student_courses sc2 ON sc1.student_id = sc2.student_id
            INNER JOIN courses c ON sc2.course_id = c.id
            WHERE sc1.course_id = %s 
              AND sc2.course_id != %s
              AND sc1.is_active = TRUE 
              AND sc2.is_active = TRUE
            GROUP BY sc2.course_id, c.code, c.name
            HAVING COUNT(DISTINCT sc1.student_id) >= %s
            ORDER BY overlap_count DESC
        """
        rows, columns = self._execute_query(query, (course_id, course_id, min_overlap))
        
        result = []
        for row in rows:
            data = dict(zip(columns, row))
            result.append({
                'course_id': data['course_id'],
                'course_code': data['course_code'],
                'course_name': data['course_name'],
                'overlap_count': data['overlap_count']
            })
        
        return result
    
    def delete_by_course(self, course_id: int) -> int:
        """Belirli bir dersin tüm öğrenci ilişkilerini siler (soft delete)"""
        query = "UPDATE student_courses SET is_active = FALSE WHERE course_id = %s"
        return self._execute_non_query(query, (course_id,))
    
    def delete_by_student(self, student_id: int) -> int:
        """Belirli bir öğrencinin tüm ders ilişkilerini siler (soft delete)"""
        query = "UPDATE student_courses SET is_active = FALSE WHERE student_id = %s"
        return self._execute_non_query(query, (student_id,))
