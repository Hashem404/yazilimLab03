# Repositories Katmanı Dokümantasyonu

Bu dokümantasyon, veri erişim katmanındaki repository sınıflarını analiz eder.

## İçindekiler
- [Genel Bakış](#genel-bakış)
- [BaseRepository](#baserepository)
- [UserRepository](#userrepository)
- [FacultyRepository](#facultyrepository)
- [DepartmentRepository](#departmentrepository)
- [LecturerRepository](#lecturerrepository)
- [CourseRepository](#courserepository)
- [ClassroomRepository](#classroomrepository)
- [StudentRepository](#studentrepository)
- [StudentCourseRepository](#studentcourserepository)
- [ExamScheduleRepository](#examschedulerepository)
- [SQL Sorgu Yapısı](#sql-sorgu-yapısı)
- [Olası Hatalar](#olası-hatalar)

---

## Genel Bakış

Repositories katmanı, veritabanı işlemlerini yönetir. Her repository:

- [`BaseRepository`](../src/repositories/base_repository.py:1) sınıfından türer
- CRUD operasyonlarını sağlar
- Model dönüşümlerini yapar
- Bağlantı havuzunu kullanır

**Dosya Konumu**: [`src/repositories/`](../src/repositories/)

```
src/repositories/
├── __init__.py
├── base_repository.py      # Temel repository sınıfı
├── user_repository.py       # Kullanıcı işlemleri
├── faculty_repository.py    # Fakülte işlemleri
���── department_repository.py # Bölüm işlemleri
├── lecturer_repository.py   # Öğretim üyesi işlemleri
├── course_repository.py     # Ders işlemleri
├── classroom_repository.py  # Derslik işlemleri
└── exam_schedule_repository.py # Sınav programı işlemleri
```

---

## BaseRepository

**Dosya**: [`src/repositories/base_repository.py`](../src/repositories/base_repository.py:1)

### Sınıf Yapısı

```python
class BaseRepository(ABC, Generic[T]):
    def __init__(self):
        self.table_name: str = ""
    
    @abstractmethod
    def _row_to_entity(self, row: tuple, columns: List[str]) -> T:
        pass
    
    @abstractmethod
    def _entity_to_values(self, entity: T) -> tuple:
        pass
```

### Özellikler

| Özellik | Tip | Açıklama |
|---------|-----|----------|
| `table_name` | str | Tablo adı |

### Soyut Metotlar

| Metot | Açıklama |
|-------|----------|
| `_row_to_entity(row, columns)` | DB satırını modele dönüştürür |
| `_entity_to_values(entity)` | Modeli SQL değerlerine dönüştürür |

### Temel CRUD Metotları

#### `_execute_query(query, params) -> List[tuple]`
SELECT sorgusu çalıştırır.

```python
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
```

#### `_execute_non_query(query, params, return_id) -> Optional[int]`
INSERT, UPDATE, DELETE sorgusu çalıştırır.

```python
def _execute_non_query(self, query: str, params: tuple = None, return_id: bool = False) -> Optional[int]:
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
```

### Genel CRUD Metotları

| Metot | Açıklama |
|-------|----------|
| `get_all()` | Tüm kayıtları getirir |
| `get_by_id(id)` | ID'ye göre kayıt getirir |
| `delete(id)` | Kayıt siler |
| `count()` | Toplam kayıt sayısı |
| `exists(id)` | Kayıt var mı? |
| `search(column, value)` | Kolonda arama yapar (ILIKE) |

---

## UserRepository

**Dosya**: [`src/repositories/user_repository.py`](../src/repositories/user_repository.py:1)

### CRUD Metotları

#### `create(user: User) -> int`
```python
def create(self, user: User) -> int:
    query = """
        INSERT INTO users (username, password_hash, email, first_name, last_name, role, department_id, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
```

#### `update(user: User) -> bool`
```python
def update(self, user: User) -> bool:
    query = """
        UPDATE users
        SET username = %s, password_hash = %s, email = %s, first_name = %s,
            last_name = %s, role = %s, department_id = %s, is_active = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """
```

### Özel Sorgu Metotları

| Metot | Açıklama | SQL |
|-------|----------|-----|
| `get_by_username(username)` | Kullanıcı adına göre getir | `WHERE username = %s` |
| `get_by_email(email)` | E-postaya göre getir | `WHERE email = %s` |
| `get_active_users()` | Aktif kullanıcılar | `WHERE is_active = TRUE` |
| `get_by_role(role)` | Role göre getir | `WHERE role = %s` |
| `update_last_login(user_id)` | Son girişi güncelle | `UPDATE users SET last_login = ...` |
| `update_password(user_id, hash)` | Şifre güncelle | `UPDATE users SET password_hash = ...` |
| `deactivate(user_id)` | Hesabı devre dışı bırak | `UPDATE users SET is_active = FALSE` |
| `activate(user_id)` | Hesabı aktif et | `UPDATE users SET is_active = TRUE` |
| `username_exists(username, exclude_id)` | Kullanıcı adı kontrolü | `SELECT EXISTS(...)` |
| `email_exists(email, exclude_id)` | E-posta kontrolü | `SELECT EXISTS(...)` |
| `authenticate(username, hash)` | Kimlik doğrulama | `WHERE username = %s AND password_hash = %s` |

### authenticate() Detaylı

```python
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
        self.update_last_login(user.id)  # Otomatik güncelle
        return user
    return None
```

---

## FacultyRepository

**Dosya**: [`src/repositories/faculty_repository.py`](../src/repositories/faculty_repository.py:1)

### CRUD Metotları

| Metot | Açıklama |
|-------|----------|
| `create(faculty)` | Yeni fakülte ekler |
| `update(faculty)` | Fakülte günceller |
| `delete(id)` | Fakülte siler |

### Özel Sorgu Metotları

| Metot | Açıklama |
|-------|----------|
| `get_by_code(code)` | Koda göre fakülte |
| `get_all_active()` | Aktif fakülteler |
| `get_with_departments()` | Fakülteler ve bölümleri (JOIN) |

### get_with_departments() SQL

```sql
SELECT f.id, f.name as faculty_name, f.code as faculty_code,
       d.id as department_id, d.name as department_name, d.code as department_code
FROM faculties f
LEFT JOIN departments d ON f.id = d.faculty_id
ORDER BY f.name, d.name
```

---

## DepartmentRepository

**Dosya**: [`src/repositories/department_repository.py`](../src/repositories/department_repository.py:1)

### CRUD Metotları

| Metot | Açıklama |
|-------|----------|
| `create(department)` | Yeni bölüm ekler |
| `update(department)` | Bölüm günceller |
| `delete(id)` | Bölüm siler |

### Özel Sorgu Metotları

| Metot | Açıklama | SQL |
|-------|----------|-----|
| `get_by_code(code)` | Koda göre bölüm | `WHERE code = %s` |
| `get_by_faculty_id(faculty_id)` | Fakülteye göre bölümler | JOIN ile faculty_name |
| `get_all_with_faculty()` | Tüm bölümler ve fakülteleri | LEFT JOIN faculties |

### get_all_with_faculty() SQL

```sql
SELECT d.*, f.name as faculty_name
FROM departments d
LEFT JOIN faculties f ON d.faculty_id = f.id
ORDER BY f.name, d.name
```

---

## LecturerRepository

**Dosya**: [`src/repositories/lecturer_repository.py`](../src/repositories/lecturer_repository.py:1)

### CRUD Metotları

| Metot | Açıklama |
|-------|----------|
| `create(lecturer)` | Yeni öğretim üyesi ekler |
| `update(lecturer)` | Öğretim üyesi günceller |
| `delete(id)` | Öğretim üyesi siler |

### Özel Sorgu Metotları

| Metot | Açıklama | SQL |
|-------|----------|-----|
| `get_by_department_id(dept_id)` | Bölüme göre hocalar | JOIN dept + faculty |
| `get_all_with_details()` | Tüm hocalar detaylı | 2x LEFT JOIN |
| `get_by_email(email)` | E-postaya göre | `WHERE email = %s` |
| `get_available_on_day(day)` | Günde müsait hocalar | `WHERE %s = ANY(available_days)` |
| `update_available_days(id, days)` | Müsait günleri güncelle | UPDATE available_days |

### get_all_with_details() SQL

```sql
SELECT l.*, d.name as department_name, f.name as faculty_name
FROM lecturers l
LEFT JOIN departments d ON l.department_id = d.id
LEFT JOIN faculties f ON d.faculty_id = f.id
ORDER BY f.name, d.name, l.last_name, l.first_name
```

### Array Kolon Sorgusu

```sql
-- PostgreSQL array sorgusu
WHERE %s = ANY(l.available_days)
```

---

## CourseRepository

**Dosya**: [`src/repositories/course_repository.py`](../src/repositories/course_repository.py:1)

### CRUD Metotları

| Metot | Açıklama |
|-------|----------|
| `create(course)` | Yeni ders ekler (artık `required_room_type` alanı dahil) |
| `update(course)` | Ders günceller |
| `delete(id)` | Ders siler |

### Özel Sorgu Metotları

| Metot | Açıklama |
|-------|----------|
| `get_by_code(code)` | Koda göre ders |
| `get_by_department_id(dept_id)` | Bölüme göre dersler |
| `get_by_lecturer_id(lecturer_id)` | Hocaya göre dersler |
| `get_all_with_details()` | Tüm dersler detaylı |
| `get_by_year_semester(year, semester)` | Yıl/döneme göre |
| `get_unscheduled_courses(exam_type)` | Planlanmamış dersler |

### Oda Tipi Alanı (YENİ ⭐)

```sql
-- courses tablosuna eklenen alan
ALTER TABLE courses ADD COLUMN required_room_type VARCHAR(20) DEFAULT 'ANY';

-- Geçerli oda tipleri
-- 'STANDART', 'LAB', 'OFIS', 'DEKANLIK', 'BILGISALONU', 'KONFERANS', 'ANY'
-- 'ANY' = Herhangi bir oda tipi uygun
```

### Sınav Süresi Alanı (GENİŞLETİLDİ ⭐)

```python
# Artık 4-8 saatlik sınavlar da destekleniyor
# Geçerli sınav süreleri: 30, 60, 90, 120, 240, 360, 480 dakika
exam_duration INT DEFAULT 60
```

### get_all_with_details() SQL

```sql
SELECT c.*, d.name as department_name,
       CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
       f.name as faculty_name
FROM courses c
LEFT JOIN departments d ON c.department_id = d.id
LEFT JOIN lecturers l ON c.lecturer_id = l.id
LEFT JOIN faculties f ON d.faculty_id = f.id
ORDER BY f.name, d.name, c.year, c.semester, c.code
```

### get_unscheduled_courses() SQL

```sql
SELECT c.*, d.name as department_name,
       CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
       f.name as faculty_name
FROM courses c
LEFT JOIN departments d ON c.department_id = d.id
LEFT JOIN lecturers l ON c.lecturer_id = l.id
LEFT JOIN faculties f ON d.faculty_id = f.id
WHERE c.id NOT IN (
    SELECT DISTINCT course_id FROM exam_schedule
    WHERE status != 'cancelled'
    AND exam_type = %s
)
AND c.has_exam = TRUE
AND c.exam_duration > 0
ORDER BY f.name, d.name, c.year, c.semester, c.code
```

---

## ClassroomRepository

**Dosya**: [`src/repositories/classroom_repository.py`](../src/repositories/classroom_repository.py:1)

### CRUD Metotları

| Metot | Açıklama |
|-------|----------|
| `create(classroom)` | Yeni derslik ekler (artık `room_type` alanı dahil) |
| `update(classroom)` | Derslik günceller |
| `delete(id)` | Derslik siler |

### Özel Sorgu Metotları

| Metot | Açıklama |
|-------|----------|
| `get_by_faculty(faculty_id)` | Fakülteye göre derslikler |
| `get_by_min_capacity(min)` | Minimum kapasiteye göre |
| `get_available_for_exam(date, start, end, room_type)` | Sınav için uygun derslikler (YENİ: oda tipi filtresi) |
| `get_faculties()` | Derslik olan fakülteler |
| `get_suitable_classrooms(min_cap, room_type)` | Sınava uygun derslikler (YENİ: oda tipi filtresi) |
| `get_exam_suitable_classrooms(room_type)` | `is_suitable = TRUE` olanlar (YENİ: oda tipi filtresi) |
| `get_available_classrooms(date, start, end)` | Müsait derslikler |
| `get_by_room_type(room_type)` | **YENİ**: Belirli tipteki derslikleri getirir |
| `get_by_types(room_types)` | **YENİ**: Birden fazla tipteki derslikleri getirir |

### Oda Tipi Alanı (YENİ ⭐)

```sql
-- classrooms tablosuna eklenen alan
ALTER TABLE classrooms ADD COLUMN room_type VARCHAR(20) DEFAULT 'STANDART';

-- Geçerli oda tipleri
-- 'STANDART', 'LAB', 'OFIS', 'DEKANLIK', 'BILGISALONU', 'KONFERANS'
```

### get_by_room_type() SQL (YENİ)

```sql
SELECT c.*, f.name as faculty_name
FROM classrooms c
LEFT JOIN faculties f ON c.faculty_id = f.id
WHERE c.room_type = %s
AND c.is_active = TRUE
ORDER BY c.capacity
```

### get_available_for_exam() SQL

```sql
SELECT c.id, c.name, c.faculty_id, c.capacity, c.has_computer, c.is_suitable,
       f.name as faculty_name
FROM classrooms c
LEFT JOIN faculties f ON c.faculty_id = f.id
WHERE c.is_suitable = TRUE
AND c.id NOT IN (
    SELECT es.classroom_id FROM exam_schedule es
    WHERE es.exam_date = %s
    AND es.status != 'cancelled'
    AND (
        (es.start_time <= %s AND es.end_time > %s)
        OR (es.start_time < %s AND es.end_time >= %s)
        OR (es.start_time >= %s AND es.end_time <= %s)
    )
)
ORDER BY c.capacity
```

### Zaman Çakışma Kontrolü

```sql
-- Start1 <= End2 AND End1 > Start2
-- Bu formül zaman çakışmasını kontrol eder
(es.start_time <= %s AND es.end_time > %s)
```

---

## StudentRepository

**Dosya**: [`src/repositories/student_repository.py`](../src/repositories/student_repository.py:1)

### Amaç
Öğrenci verilerini yönetir ve öğrenci bazlı çakışma kontrolü için gerekli sorguları sağlar.

### Sınıf Yapısı

```python
class StudentRepository(BaseRepository[Student]):
    def __init__(self):
        super().__init__()
        self.table_name = "students"
```

### CRUD Metotları

| Metot | Açıklama |
|-------|----------|
| `create(student)` | Yeni öğrenci ekler (UPSERT) |
| `create_batch(students)` | Çoklu öğrenci ekler (batch UPSERT) |
| `update(student)` | Öğrenci günceller |
| `delete(id)` | Öğrenci siler |

### Özel Sorgu Metotları

| Metot | Açıklama | SQL |
|-------|----------|-----|
| `get_by_student_number(number)` | Öğrenci numarasına göre | `WHERE student_number = %s` |
| `get_by_email(email)` | **YENI**: E-postaya göre | `WHERE email = %s` |
| `get_by_department_id(dept_id)` | Bölüme göre öğrenciler | JOIN dept + faculty |
| `get_all_with_details()` | Tüm öğrenciler detaylı | 2x LEFT JOIN |
| `delete_by_department(dept_id)` | Bölüm öğrencilerini sil | Soft delete |

### UPSERT Özelliği

```python
def create(self, student: Student) -> int:
    query = """
        INSERT INTO students (student_number, first_name, last_name, email,
                             department_id, year, is_active)
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
```

### Özel Sorgu Metotları

| Metot | Açıklama | SQL |
|-------|----------|-----|
| `get_by_student_number(number)` | Öğrenci numarasına göre (JOIN ile) | `WHERE student_number = %s` |
| `get_by_department_id(dept_id)` | Bölüme göre öğrenciler | `WHERE department_id = %s` |
| `get_all_with_details()` | Tüm öğrenciler detaylı | 2x LEFT JOIN |
| `get_student_numbers_by_course(course_id)` | Dersi alan öğrencilerin numaraları | student_courses JOIN |
| `get_student_numbers_by_courses(course_ids)` | Çoklu ders için öğrenci numaraları | ANY ile batch sorgu |
| `delete_by_department(dept_id)` | Bölüm öğrencilerini soft delete | `UPDATE is_active = FALSE` |

### get_all_with_details() SQL

```sql
SELECT s.*, d.name as department_name, f.name as faculty_name
FROM students s
LEFT JOIN departments d ON s.department_id = d.id
LEFT JOIN faculties f ON d.faculty_id = f.id
WHERE s.is_active = TRUE
ORDER BY d.name, s.year, s.student_number
```

### Öğrenci Bazlı Çakışma Sorguları

#### `get_student_numbers_by_course(course_id)` - Tek Ders

```python
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
```

#### `get_student_numbers_by_courses(course_ids)` - Çoklu Ders

```python
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
```

### create_batch() Metodu

```python
def create_batch(self, students: List[Student]) -> int:
    """Toplu öğrenci kaydı için optimize edilmiş metot"""
    if not students:
        return 0
    
    query = """
        INSERT INTO students (student_number, first_name, last_name, email,
                             department_id, year, is_active)
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
```

---

## StudentCourseRepository

**Dosya**: [`src/repositories/student_repository.py`](../src/repositories/student_repository.py:166)

### Amaç
Öğrenci-ders ilişkilerini yönetir ve çakışma kontrolü için gerekli sorguları sağlar.

### Sınıf Yapısı

```python
class StudentCourseRepository(BaseRepository[StudentCourse]):
    def __init__(self):
        super().__init__()
        self.table_name = "student_courses"
        self.connection = connection
```

### CRUD Metotları

| Metot | Açıklama |
|-------|----------|
| `create(student_course)` | Yeni kayıt ekler |
| `create_batch(student_courses)` | Çoklu kayıt ekler (batch) |
| `delete(id)` | Kayıt siler |
| `delete_by_student(student_id)` | Öğrencinin tüm kayıtlarını siler |
| `delete_by_course(course_id)` | Dersin tüm kayıtlarını siler |

### Öğrenci Çakışma Kontrolü Metotları

| Metot | Açıklama |
|-------|----------|
| `get_student_ids_by_course(course_id)` | Dersteki öğrenci ID'leri (Set) |
| `check_student_overlap(course_id1, course_id2)` | İki ders arası çakışma sayısı |
| `get_conflicting_courses(course_id, min_overlap)` | Çakışan dersleri listeler |
| `get_courses_by_student(student_id)` | Öğrencinin dersleri |
| `get_student_courses_with_details(student_id)` | Öğrenci dersleri detaylı |

### get_student_ids_by_course() Metodu

```python
def get_student_ids_by_course(self, course_id: int) -> Set[int]:
    """
    Belirli bir dersi alan öğrenci ID'lerini döndürür
    Çakışma kontrolü için optimize edilmiş Set dönüşümü
    """
    query = """
        SELECT student_id
        FROM student_courses
        WHERE course_id = %s AND is_active = TRUE
    """
    rows, _ = self._execute_query(query, (course_id,))
    return {row[0] for row in rows}
```

### check_student_overlap() Metodu

```python
def check_student_overlap(self, course_id1: int, course_id2: int) -> int:
    """
    İki ders arasındaki ortak öğrenci sayısını döndürür
    Kesişim kümesi boyutunu SQL ile hesaplar
    """
    query = """
        SELECT COUNT(DISTINCT sc1.student_id) as overlap_count
        FROM student_courses sc1
        INNER JOIN student_courses sc2 ON sc1.student_id = sc2.student_id
        WHERE sc1.course_id = %s
        AND sc2.course_id = %s
        AND sc1.is_active = TRUE
        AND sc2.is_active = TRUE
    """
    rows, _ = self._execute_query(query, (course_id1, course_id2))
    return rows[0][0] if rows else 0
```

### get_conflicting_courses() Metodu

```python
def get_conflicting_courses(self, course_id: int, min_overlap: int = 1) -> List[Tuple[int, int]]:
    """
    Belirli bir dersle çakışan dersleri listeler
    Returns: List[(course_id, overlap_count), ...]
    """
    query = """
        SELECT sc2.course_id, COUNT(DISTINCT sc1.student_id) as overlap_count
        FROM student_courses sc1
        INNER JOIN student_courses sc2 ON sc1.student_id = sc2.student_id
        WHERE sc1.course_id = %s
        AND sc2.course_id != %s
        AND sc1.is_active = TRUE
        AND sc2.is_active = TRUE
        GROUP BY sc2.course_id
        HAVING COUNT(DISTINCT sc1.student_id) >= %s
        ORDER BY overlap_count DESC
    """
    rows, _ = self._execute_query(query, (course_id, course_id, min_overlap))
    return [(row[0], row[1]) for row in rows]
```

### create_batch() Metodu

```python
def create_batch(self, student_courses: List[StudentCourse]) -> int:
    """Çoklu öğrenci-ders ilişkisi insert işlemi"""
    query = """
        INSERT INTO student_courses (student_id, course_id, semester, is_active)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (student_id, course_id)
        DO UPDATE SET is_active = TRUE, semester = EXCLUDED.semester
    """
    data = [(sc.student_id, sc.course_id, sc.semester, sc.is_active)
            for sc in student_courses]
    return self._execute_batch_non_query(query, data)
```

### Öğrenci Bazlı Çakışma Kontrolü Algoritması

Bu repository, **öğrenci numaraları üzerinden çakışma kontrolü** yapar:

```python
# Örnek kullanım:
student_repo = StudentCourseRepository(conn)

# Ders A'nın öğrencileri
students_A = student_repo.get_student_ids_by_course(course_A_id)
# Örn: {101, 102, 103, 104}

# Ders B'nin öğrencileri
students_B = student_repo.get_student_ids_by_course(course_B_id)
# Örn: {103, 104, 105, 106}

# Kesişim kümesi
intersection = students_A & students_B
# {103, 104}

if intersection:
    # Çakışma var! Bu iki ders aynı saatte sınav olamaz
    print(f"Ortak öğrenci sayısı: {len(intersection)}")
```

---

## ExamScheduleRepository

**Dosya**: [`src/repositories/exam_schedule_repository.py`](../src/repositories/exam_schedule_repository.py:1)

### CRUD Metotları

| Metot | Açıklama |
|-------|----------|
| `create(exam_schedule)` | Yeni sınav programı ekler |
| `update(exam_schedule)` | Sınav programı günceller |
| `delete(id)` | Sınav programı siler |

### Tarih Bazlı Sorgular

| Metot | Açıklama |
|-------|----------|
| `get_by_date(exam_date)` | Tarihteki sınavlar |
| `get_by_date_range(start, end)` | Tarih aralığındaki sınavlar |
| `get_by_course_id(course_id)` | Derse göre sınavlar |
| `get_by_classroom_id(classroom_id)` | Dersliğe göre sınavlar |
| `get_all_with_details()` | Tüm sınavlar detaylı |
| `get_by_department_id(dept_id)` | Bölüme göre sınavlar |
| `get_by_classroom_and_date(classroom_id, date)` | Derslik-tarih sınavları |
| `get_by_department_and_date(dept_id, date)` | Bölüm-tarih sınavları |
| `get_by_lecturer_and_date(lecturer_id, date)` | Hoca-tarih sınavları |
| `get_by_faculty_id(faculty_id)` | Fakülteye göre sınavlar |

### Kullanıcı Bazlı Sorgular ⭐ YENİ

| Metot | Açıklama |
|-------|----------|
| `get_by_student_id(student_id)` | Öğrencinin aldığı derslerin sınavları |
| `get_by_student_number(student_number)` | Öğrenci numarasına göre sınavlar |
| `get_by_lecturer_id_all(lecturer_id)` | Hocanın verdiği derslerin tüm sınavları |

#### get_by_student_id() SQL

```sql
SELECT DISTINCT es.*, c.code as course_code, c.name as course_name, c.student_count,
       cl.name as classroom_name, f.name as faculty_name,
       CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
       d.name as department_name
FROM exam_schedule es
INNER JOIN student_courses sc ON es.course_id = sc.course_id
LEFT JOIN courses c ON es.course_id = c.id
LEFT JOIN classrooms cl ON es.classroom_id = cl.id
LEFT JOIN faculties f ON cl.faculty_id = f.id
LEFT JOIN lecturers l ON c.lecturer_id = l.id
LEFT JOIN departments d ON c.department_id = d.id
WHERE sc.student_id = %s
  AND sc.is_active = TRUE
  AND es.status != 'cancelled'
ORDER BY es.exam_date, es.start_time
```

#### get_by_lecturer_id_all() SQL

```sql
SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
       cl.name as classroom_name, f.name as faculty_name,
       CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
       d.name as department_name
FROM exam_schedule es
LEFT JOIN courses c ON es.course_id = c.id
LEFT JOIN classrooms cl ON es.classroom_id = cl.id
LEFT JOIN faculties f ON cl.faculty_id = f.id
LEFT JOIN lecturers l ON c.lecturer_id = l.id
LEFT JOIN departments d ON c.department_id = d.id
WHERE c.lecturer_id = %s
  AND es.status != 'cancelled'
ORDER BY es.exam_date, es.start_time
```

### get_by_department_and_date() SQL

```sql
SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
       cl.name as classroom_name, f.name as faculty_name,
       CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
       d.name as department_name, c.year as course_year
FROM exam_schedule es
LEFT JOIN courses c ON es.course_id = c.id
LEFT JOIN classrooms cl ON es.classroom_id = cl.id
LEFT JOIN faculties f ON cl.faculty_id = f.id
LEFT JOIN lecturers l ON c.lecturer_id = l.id
LEFT JOIN departments d ON c.department_id = d.id
WHERE c.department_id = %s
AND es.exam_date = %s
AND es.status != 'cancelled'
ORDER BY es.start_time
```

### Çakışma Kontrolü Metotları

| Metot | Açıklama |
|-------|----------|
| `check_conflict(classroom_id, date, start, end, exclude_id)` | Derslik çakışması |
| `check_course_exam_exists(course_id, exam_type, ...)` | Ders için sınav var mı? |
| `check_student_conflict(dept_id, year, date, start, end, ...)` | Öğrenci çakışması |
| `check_lecturer_conflict(lecturer_id, date, start, end, ...)` | Hoca çakışması |

### check_student_conflict() SQL

```sql
SELECT es.*, c.code as course_code, c.name as course_name, c.student_count,
       cl.name as classroom_name, f.name as faculty_name,
       CONCAT(l.title, ' ', l.first_name, ' ', l.last_name) as lecturer_name,
       d.name as department_name, c.year as course_year
FROM exam_schedule es
LEFT JOIN courses c ON es.course_id = c.id
LEFT JOIN classrooms cl ON es.classroom_id = cl.id
LEFT JOIN faculties f ON cl.faculty_id = f.id
LEFT JOIN lecturers l ON c.lecturer_id = l.id
LEFT JOIN departments d ON c.department_id = d.id
WHERE c.department_id = %s
AND c.year = %s
AND es.exam_date = %s
AND es.status != 'cancelled'
AND es.id != COALESCE(%s, -1)
AND c.id != COALESCE(%s, -1)
AND (
    (es.start_time <= %s AND es.end_time > %s)
    OR (es.start_time < %s AND es.end_time >= %s)
    OR (es.start_time >= %s AND es.end_time <= %s)
)
ORDER BY es.start_time
```

### Yönetim Metotları

| Metot | Açıklama |
|-------|----------|
| `update_status(exam_id, status)` | Durumu güncelle (planned/confirmed/cancelled) |
| `delete_all()` | Tüm sınavları sil |
| `delete_planned()` | Planlanan sınavları sil |
| `get_by_status(status)` | Duruma göre sınavlar |

---

## SQL Sorgu Yapısı

### Parametreli Sorgular

Tüm sorgular parametreli olarak kullanılır (SQL Injection koruması):

```python
# ✅ Doğru
query = "SELECT * FROM users WHERE username = %s"
self._execute_query(query, (username,))

# ❌ Yanlış
query = f"SELECT * FROM users WHERE username = '{username}'"
self._execute_query(query)
```

### JOIN Kullanımı

```sql
-- LEFT JOIN: Tüm kayıtlar + eşleşenler
SELECT c.*, d.name as department_name
FROM courses c
LEFT JOIN departments d ON c.department_id = d.id

-- INNER JOIN: Sadece eşleşen kayıtlar
SELECT c.*, d.name as department_name
FROM courses c
INNER JOIN departments d ON c.department_id = d.id
```

### Array Kolonlar

```sql
-- PostgreSQL array kolonu
available_days TEXT[] DEFAULT '{Pazartesi,Salı,Çarşamba,Perşembe,Cuma}'

-- Array içinde arama
WHERE 'Pazartesi' = ANY(available_days)
```

### Zaman Çakışma Kontrolü

```sql
-- İki zaman aralığı çakışıyor mu?
-- (Start1 <= End2) AND (End1 > Start2)

WHERE (es.start_time <= %s AND es.end_time > %s)
   OR (es.start_time < %s AND es.end_time >= %s)
   OR (es.start_time >= %s AND es.end_time <= %s)
```

### EXISTS Kullanımı

```sql
-- Kayıt var mı kontrolü
SELECT EXISTS(
    SELECT 1 FROM users
    WHERE username = %s
    AND id != COALESCE(%s, -1)
)
```

### ORDER BY ve LIMIT

```sql
-- Sıralama
ORDER BY f.name, d.name, c.year, c.semester, c.code

-- LIMIT (Python tarafında)
rows[:limit]  # İlk N kayıt
```

---

## Olası Hatalar

### 1. Bağlantı Havuzu Sorunları

#### Hata: Pool Exhausted
```python
# Hata: Tüm bağlantılar kullanımda
psycopg2.pool.PoolError: connection pool exhausted

# Çözüm:
# 1. Bağlantıları düzgün release edin
try:
    conn = get_connection()
    # işlemler
finally:
    release_connection(conn)

# 2. Havuz boyutunu artırın
# database/core/connection.py: maxconn=10 -> 20
```

### 2. Transaction Sorunları

#### Hata: Deadlock
```python
# Hata: İki transaction birbirini bekliyor
psycopg2.extensions.TransactionRollbackError: deadlock detected

# Çözüm:
# 1. Her zaman aynı sıralamada tablolara erişin
# 2. Transaction'ları kısa tutun
# 3. Retry mekanizması ekleyin
```

#### Hata: Implicit Rollback
```python
# Hata commit yapılmadan bağlantı kapatılırsa
conn.close()  # Değişiklikler kaybolur

# Çözüm: _execute_non_query'de commit var
# Manuel kullanımda unutmayın:
conn.commit()
```

### 3. Tip Dönüşüm Hataları

#### Hata: Array Parsing
```python
# PostgreSQL: '{Pazartesi,Salı}'
# Python'da parse gerekli

available_days = data.get('available_days', [])
if isinstance(available_days, str):
    available_days = available_days.strip('{}').split(',')
```

#### Hata: Date/Time
```python
# Veritabanından gelen: datetime.date
# Python'da: datetime.datetime

# Çözüm:
exam_date = row[0]
if isinstance(exam_date, datetime):
    exam_date = exam_date.date()
```

### 4. N+1 Sorgu Problemi

#### Sorun
```python
# Her kayıt için ayrı sorgu
for course in courses:
    department = department_repo.get_by_id(course.department_id)  # N+1
```

#### Çözüm
```python
# JOIN ile tek sorguda
SELECT c.*, d.name as department_name
FROM courses c
LEFT JOIN departments d ON c.department_id = d.id
```

### 5. NULL Kontrolü

#### Hata
```python
# Fakülte silinirse department.faculty_id NULL olur
# faculty_name erişilirse hata

# Çözüm:
faculty_name = row.get('faculty_name') or 'Belirsiz'
```

### 6. Unique Constraint Violation

#### Hata
```python
# Aynı kod ile yeni kayıt
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint

# Çözüm:
# Repository'de kontrol edin
if self.get_by_code(course.code):
    raise ValueError("Bu kod zaten kullanılıyor")
```

### 7. Foreign Key Violation

#### Hata
```python
# İlişkili kayıt silinirse
psycopg2.errors.ForeignKeyViolation: update or delete violates foreign key constraint

# Çözüm:
# 1. Önce bağlı kayıtları silin
# 2. ON DELETE CASCADE kullanın
# 3. Soft delete kullanın (is_active=False)
```

---

## Performans Önerileri

### 1. Sorgu Optimizasyonu

```sql
-- ❌ Yavaş (LIKE başında)
WHERE name LIKE '% searchTerm %'

-- ✅ Hızlı (ILIKE ile indeks kullanımı)
WHERE name ILIKE 'searchTerm%'

-- ✅ Full Text Search
WHERE to_tsvector('turkish', name) @@ to_tsquery('turkish', 'searchTerm')
```

### 2. İndeks Kullanımı

```sql
-- Sadece WHERE'de kullanılan kolonlara indeks
CREATE INDEX idx_courses_department_id ON courses(department_id);

-- Kompozit indeks
CREATE INDEX idx_courses_department_lecturer ON courses(department_id, lecturer_id);

-- Partial indeks
CREATE INDEX idx_courses_active ON courses(code) WHERE is_active = TRUE;
```

### 3. Batch Insert

```python
# ❌ Tek tek insert
for item in items:
    repo.create(item)

# ✅ Batch insert
query = """
    INSERT INTO courses (name, code, ...)
    VALUES (%s, %s, ...), (%s, %s, ...), ...
"""
values = [(item.name, item.code, ...) for item in items]
```

### 4. Connection Pool Ayarları

```python
# Mevcut: minconn=1, maxconn=10
# Öneri (yüksek trafik için):
pool = SimpleConnectionPool(
    minconn=5,    # Minimum açık bağlantı
    maxconn=20,   # Maksimum bağlantı
)
```

---

## Örnek Kullanım

```python
from src.repositories.user_repository import UserRepository
from src.models.user import User

# Repository oluştur
user_repo = UserRepository()

# Yeni kullanıcı
user = User(
    username="test_user",
    first_name="Test",
    last_name="User",
    role="ogrenci"
)
user.set_password("password123")

# Kaydet
user_id = user_repo.create(user)

# Oku
user = user_repo.get_by_id(user_id)
print(user.full_name)

# Güncelle
user.last_name = "Updated"
user_repo.update(user)

# Ara
users = user_repo.get_by_role("ogrenci")

# Sil
user_repo.delete(user_id)
```
