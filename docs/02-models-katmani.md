# Models Katmanı Dokümantasyonu

Bu dokümantasyon, veri modellemesi katmanındaki tüm sınıfları analiz eder.

## İçindekiler
- [Genel Bakış](#genel-bakış)
- [User Model](#user-model)
- [Faculty Model](#faculty-model)
- [Department Model](#department-model)
- [Lecturer Model](#lecturer-model)
- [Course Model](#course-model)
- [Classroom Model](#classroom-model)
- [Student Model](#student-model)
- [StudentCourse Model](#studentcourse-model)
- [ExamSchedule Model](#examschedule-model)
- [Model İlişkileri](#model-ilişkileri)
- [Olası Hatalar](#olası-hatalar)

---

## Genel Bakış

Models katmanı, veritabanı tablolarını temsil eden `dataclass` tabanlı sınıfları içerir. Her model:

- `@dataclass` dekoratörü kullanır
- `to_dict()` ve `from_dict()` metodlarına sahiptir
- `__post_init__()` ile varsayılan değerleri ayarlar
- Optional türler için null güvenliği sağlar

**Dosya Konumu**: [`src/models/`](../src/models/)

```
src/models/
├── __init__.py
├── user.py              # Kullanıcı modeli
├── faculty.py           # Fakülte modeli
├── department.py        # Bölüm modeli
├── lecturer.py          # Öğretim üyesi modeli
├── course.py            # Ders modeli
├── classroom.py         # Derslik modeli
├── student.py           # Öğrenci modeli ⭐ YENİ
└── exam_schedule.py     # Sınav programı modeli
```

---

## User Model

**Dosya**: [`src/models/user.py`](../src/models/user.py:1)

### Sınıf Yapısı

```python
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
```

### Özellikler

| Özellik | Tip | Zorunlu | Açıklama |
|---------|-----|---------|----------|
| `id` | Optional[int] | Hayır | Benzersiz kimlik |
| `username` | str | Evet | Kullanıcı adı (unique) |
| `password_hash` | str | Evet | SHA256 hash |
| `email` | Optional[str] | Hayır | E-posta adresi (unique) |
| `first_name` | str | Evet | Ad |
| `last_name` | str | Evet | Soyad |
| `role` | str | Evet | Rol: admin/bolum_yetkilisi/hoca/ogrenci |
| `department_id` | Optional[int] | Hayır | Bölüm referansı |
| `is_active` | bool | Evet | Aktif mi? |
| `last_login` | Optional[datetime] | Hayır | Son giriş |
| `created_at` | Optional[datetime] | Hayır | Oluşturma tarihi |
| `updated_at` | Optional[datetime] | Hayır | Güncelleme tarihi |

### Önemli Metotlar

#### `full_name` (property)
```python
@property
def full_name(self) -> str:
    return f"{self.first_name} {self.last_name}".strip()
```

#### `set_password(password: str)`
```python
def set_password(self, password: str):
    self.password_hash = hashlib.sha256(password.encode()).hexdigest()
```
⚠️ **Güvenlik Sorunu**: SHA256 yerine bcrypt kullanılmalı.

#### `check_password(password: str) -> bool`
```python
def check_password(self, password: str) -> bool:
    return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
```

#### `has_permission(permission: str) -> bool`
Rol bazlı yetki kontrolü.

```python
permissions = {
    'admin': ['create', 'read', 'update', 'delete', 'export', 'manage_users', 'manage_all'],
    'bolum_yetkilisi': ['create', 'read', 'update', 'delete', 'export', 'manage_department'],
    'hoca': ['read', 'view_schedule'],
    'ogrenci': ['read', 'view_schedule']
}
```

#### Rol Kontrol Metotları
```python
def is_admin(self) -> bool
def is_bolum_yetkilisi(self) -> bool
def is_hoca(self) -> bool
def is_ogrenci(self) -> bool
def can_manage_department(self, department_id: int) -> bool
```

---

## Faculty Model

**Dosya**: [`src/models/faculty.py`](../src/models/faculty.py:1)

### Sınıf Yapısı

```python
@dataclass
class Faculty:
    id: Optional[int] = None
    name: str = ""
    code: str = ""
    dean_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### Özellikler

| Özellik | Tip | Açıklama |
|---------|-----|----------|
| `id` | Optional[int] | Benzersiz kimlik |
| `name` | str | Fakülte adı |
| `code` | str | Fakülte kodu (unique) |
| `dean_name` | Optional[str] | Dekan adı |
| `is_active` | bool | Aktif mi? |
| `created_at` | Optional[datetime] | Oluşturma tarihi |
| `updated_at` | Optional[datetime] | Güncelleme tarihi |

### Önemli Metotlar

```python
def __str__(self) -> str:
    return f"{self.code} - {self.name}"
```

---

## Department Model

**Dosya**: [`src/models/department.py`](../src/models/department.py:1)

### Sınıf Yapısı

```python
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
    
    # Join sonucu eklenen alanlar
    faculty_name: Optional[str] = None
```

### Özellikler

| Özellik | Tip | Açıklama |
|---------|-----|----------|
| `id` | Optional[int] | Benzersiz kimlik |
| `faculty_id` | Optional[int] | Fakülte FK |
| `name` | str | Bölüm adı |
| `code` | str | Bölüm kodu (unique) |
| `head_name` | Optional[str] | Bölüm başkanı |
| `head_of_department` | Optional[str] | Bölüm başkanı (alias) |
| `is_active` | bool | Aktif mi? |
| `faculty_name` | Optional[str] | Join ile gelen |
| `created_at` | Optional[datetime] | Oluşturma tarihi |
| `updated_at` | Optional[datetime] | Güncelleme tarihi |

### Önemli Davranış

`__post_init__`'da `head_name` ve `head_of_department` senkronize edilir:

```python
def __post_init__(self):
    if self.head_of_department and not self.head_name:
        self.head_name = self.head_of_department
    elif self.head_name and not self.head_of_department:
        self.head_of_department = self.head_name
```

---

## Lecturer Model

**Dosya**: [`src/models/lecturer.py`](../src/models/lecturer.py:1)

### Sınıf Yapısı

```python
@dataclass
class Lecturer:
    id: Optional[int] = None
    department_id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    title: str = ""
    email: Optional[str] = None
    available_days: List[str] = field(default_factory=lambda: DEFAULT_AVAILABLE_DAYS.copy())
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Join sonucu eklenen alanlar
    department_name: Optional[str] = None
    faculty_name: Optional[str] = None
```

### Sabitler

```python
DEFAULT_AVAILABLE_DAYS = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']
ALL_WEEKDAYS = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']
```

### Özellikler

| Özellik | Tip | Açıklama |
|---------|-----|----------|
| `id` | Optional[int] | Benzersiz kimlik |
| `department_id` | Optional[int] | Bölüm FK |
| `first_name` | str | Ad |
| `last_name` | str | Soyad |
| `title` | str | Unvan (Prof. Dr., Doç. Dr., vb.) |
| `email` | Optional[str] | E-posta |
| `available_days` | List[str] | Müsait günler |
| `department_name` | Optional[str] | Join ile gelen |
| `faculty_name` | Optional[str] | Join ile gelen |

### Önemli Metotlar

#### `full_name` (property)
```python
@property
def full_name(self) -> str:
    return f"{self.title} {self.first_name} {self.last_name}".strip()
```

#### `available_days_display` (property)
Günleri kısa formatta gösterir (Pzt, Sal, Çar, Per, Cum).

#### `is_available_on(day: str) -> bool`
Belirli bir günde müsait mi?

```python
def is_available_on(self, day: str) -> bool:
    return day in self.available_days
```

#### `get_unavailable_days() -> List[str]`
Müsait olmayan günleri döndürür.

---

## Course Model

**Dosya**: [`src/models/course.py`](../src/models/course.py:1)

### Sınıf Yapısı

```python
@dataclass
class Course:
    id: Optional[int] = None
    department_id: Optional[int] = None
    lecturer_id: Optional[int] = None
    code: str = ""
    name: str = ""
    credit: int = 3
    year: int = 1
    semester: int = 1
    period: Optional[int] = None
    theory_hours: int = 0
    lab_hours: int = 0
    course_type: str = "Zorunlu"
    description: Optional[str] = None
    student_count: int = 0
    lecturer_count: int = 1
    exam_type: str = "Yazılı"
    exam_duration: int = 60
    has_exam: bool = True
    required_room_type: str = "ANY"  # YENİ: Gereken oda tipi
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Join sonucu eklenen alanlar
    department_name: Optional[str] = None
    lecturer_name: Optional[str] = None
    faculty_name: Optional[str] = None
```

### Sabitler

```python
COURSE_TYPES = [
    ('Zorunlu', 'Zorunlu'),
    ('Alan Seçmeli', 'Alan Seçmeli'),
    ('Üniversite Seçmeli', 'Üniversite Seçmeli'),
    ('Proje', 'Proje')
]

EXAM_TYPES = [
    ('Yazılı', 'Yazılı'),
    ('Test', 'Test'),
    ('Uygulama', 'Uygulama'),
    ('Sözlü', 'Sözlü'),
    ('Proje', 'Proje'),
    ('Ödev', 'Ödev')
]

EXAM_DURATION_OPTIONS = [
    (30, '30 dakika'),
    (60, '60 dakika'),
    (90, '90 dakika'),
    (120, '120 dakika'),
    (240, '4 saat'),      # YENİ: Uzun sınavlar
    (360, '6 saat'),      # YENİ: Uzun sınavlar
    (480, '8 saat')       # YENİ: Uzun sınavlar
]

# YENİ: Dersin gerektirdiği oda tipi seçenekleri
REQUIRED_ROOM_TYPE_OPTIONS = [
    ('STANDART', 'Standart Derslik'),
    ('LAB', 'Laboratuvar'),
    ('OFIS', 'Ofis'),
    ('DEKANLIK', 'Dekanlık'),
    ('BILGISALONU', 'Bilgisayar Salonu'),
    ('KONFERANS', 'Konferans Salonu'),
    ('ANY', 'Herhangi Bir')
]
```

### Özellikler

| Özellik | Tip | Varsayılan | Açıklama |
|---------|-----|------------|----------|
| `id` | Optional[int] | None | Benzersiz kimlik |
| `department_id` | Optional[int] | None | Bölüm FK |
| `lecturer_id` | Optional[int] | None | Öğretim üyesi FK |
| `code` | str | "" | Ders kodu (unique) |
| `name` | str | "" | Ders adı |
| `credit` | int | 3 | Kredi |
| `year` | int | 1 | Sınıf (1-4) |
| `semester` | int | 1 | Dönem (1-2) |
| `period` | Optional[int] | None | Dönem bilgisi |
| `theory_hours` | int | 0 | Teori saati |
| `lab_hours` | int | 0 | Laboratuvar saati |
| `course_type` | str | "Zorunlu" | Ders türü |
| `student_count` | int | 0 | Öğrenci sayısı |
| `lecturer_count` | int | 1 | Öğretim üyesi sayısı |
| `exam_type` | str | "Yazılı" | Sınav türü |
| `exam_duration` | int | 60 | Sınav süresi (dk) - artık 8 saate kadar |
| `has_exam` | bool | True | Sınavı var mı? |
| `required_room_type` | str | "ANY" | Gereken oda tipi (YENİ) |

### Display Property'leri

```python
@property
def course_type_display(self) -> str:
    return COURSE_TYPE_MAP.get(self.course_type, self.course_type)

@property
def has_exam_display(self) -> str:
    return "Evet" if self.has_exam else "Hayır"

@property
def exam_type_display(self) -> str:
    if not self.has_exam:
        return "-"
    return EXAM_TYPE_MAP.get(self.exam_type, self.exam_type)

@property
def exam_duration_display(self) -> str:
    if not self.has_exam or self.exam_duration == 0:
        return "-"
    return f"{self.exam_duration} dk"

@property
def required_room_type_display(self) -> str:  # YEN��
    return REQUIRED_ROOM_TYPE_MAP.get(self.required_room_type, self.required_room_type)
```

---

## Classroom Model

**Dosya**: [`src/models/classroom.py`](../src/models/classroom.py:1)

### Sınıf Yapısı

```python
@dataclass
class Classroom:
    id: Optional[int] = None
    name: str = ""
    faculty_id: Optional[int] = None
    capacity: int = 0
    has_computer: bool = False
    is_suitable: bool = True
    room_type: str = "STANDART"  # YENİ: Oda tipi
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Join sonucu eklenen alanlar
    faculty_name: Optional[str] = None
```

### Sabitler (YENİ)

```python
CLASSROOM_TYPES = [
    ('STANDART', 'Standart Derslik'),
    ('LAB', 'Laboratuvar'),
    ('OFIS', 'Ofis'),
    ('DEKANLIK', 'Dekanlık'),
    ('BILGISALONU', 'Bilgisayar Salonu'),
    ('KONFERANS', 'Konferans Salonu')
]
```

### Özellikler

| Özellik | Tip | Varsayılan | Açıklama |
|---------|-----|------------|----------|
| `id` | Optional[int] | None | Benzersiz kimlik |
| `name` | str | "" | Derslik adı |
| `faculty_id` | Optional[int] | None | Fakülte FK |
| `capacity` | int | 0 | Kapasite |
| `has_computer` | bool | False | Bilgisayarlı mı? |
| `is_suitable` | bool | True | Sınav için uygun mu? |
| `room_type` | str | "STANDART" | Oda tipi (YENİ) |
| `faculty_name` | Optional[str] | None | Join ile gelen |

### Display Property'leri

```python
@property
def room_type_display(self) -> str:  # YENİ
    return CLASSROOM_TYPE_MAP.get(self.room_type, self.room_type)

def __str__(self) -> str:
    faculty_display = self.faculty_name if self.faculty_name else "Belirsiz"
    suitable_status = "✓" if self.is_suitable else "✗"
    type_display = self.room_type_display  # YENİ
    return f"{faculty_display} - {self.name} ({type_display}, Kapasite: {self.capacity}, Sınav Uygun: {suitable_status})"
```

---

## Student Model

**Dosya**: [`src/models/student.py`](../src/models/student.py:1)

### Amaç
Üniversitede öğrenim gören öğrencileri temsil eder. Her öğrencinin benzersiz bir numarası vardır.

### Sınıf Yapısı

```python
@dataclass
class Student:
    id: Optional[int] = None
    student_number: str = ""
    first_name: str = ""
    last_name: str = ""
    email: Optional[str] = None
    department_id: Optional[int] = None
    year: int = 1
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Join sonucu eklenen alanlar
    department_name: Optional[str] = None
    faculty_name: Optional[str] = None
```

### Özellikler

| Özellik | Tip | Varsayılan | Açıklama |
|---------|-----|------------|----------|
| `id` | Optional[int] | None | Benzersiz kimlik |
| `student_number` | str | "" | Öğrenci numarası (unique) |
| `first_name` | str | "" | Ad |
| `last_name` | str | "" | Soyad |
| `email` | Optional[str] | None | E-posta adresi |
| `department_id` | Optional[int] | None | Bölüm FK |
| `year` | int | 1 | Sınıf (1-4) |
| `is_active` | bool | True | Aktif mi? |
| `department_name` | Optional[str] | None | Join ile gelen |
| `faculty_name` | Optional[str] | None | Join ile gelen |

### Önemli Metotlar

#### `full_name` (property)
```python
@property
def full_name(self) -> str:
    return f"{self.first_name} {self.last_name}".strip()
```

#### `__post_init__`
```python
def __post_init__(self):
    if self.created_at is None:
        self.created_at = datetime.now()
    if self.updated_at is None:
        self.updated_at = datetime.now()
```

#### `__str__` (method)
```python
def __str__(self) -> str:
    dept_info = self.department_name if self.department_name else f"Bölüm ID: {self.department_id}"
    return f"{self.student_number} - {self.full_name} ({dept_info}, {self.year}. Sınıf)"
```

#### Serileştirme Metotları

```python
def to_dict(self) -> dict:
    """Modeli sözlüğe dönüştürür"""

@classmethod
def from_dict(cls, data: dict) -> 'Student':
    """Sözlükten model oluşturur"""
```

---

## StudentCourse Model

**Dosya**: [`src/models/student.py`](../src/models/student.py:80)

### Amaç
Hangi öğrencinin hangi dersleri aldığını tutar. Öğrenci bazlı çakışma kontrolü için kullanılır.

### Sınıf Yapısı

```python
@dataclass
class StudentCourse:
    id: Optional[int] = None
    student_id: Optional[int] = None
    course_id: Optional[int] = None
    semester: Optional[str] = None  # Örn: "2023-2024 Güz"
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    # Join sonucu eklenen alanlar
    student_number: Optional[str] = None
    student_name: Optional[str] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    department_id: Optional[int] = None
    course_year: Optional[int] = None
```

### Özellikler

| Özellik | Tip | Açıklama |
|---------|-----|----------|
| `id` | Optional[int] | Benzersiz kimlik |
| `student_id` | Optional[int] | Öğrenci FK |
| `course_id` | Optional[int] | Ders FK |
| `semester` | Optional[str] | Dönem (örn: "2024-2025 Güz") |
| `is_active` | bool | Aktif mi? |
| `student_number` | Optional[str] | Join ile gelen |
| `student_name` | Optional[str] | Join ile gelen |
| `course_code` | Optional[str] | Join ile gelen |
| `course_name` | Optional[str] | Join ile gelen |
| `department_id` | Optional[int] | Join ile gelen |
| `course_year` | Optional[int] | Ders yılı (1-4) |

### Unique Constraint

```sql
UNIQUE(student_id, course_id)
```
Bir öğrenci aynı dersi sadece bir kez alabilir.

### Önemli Metotlar

#### `__str__` (method)
```python
def __str__(self) -> str:
    student_info = self.student_number if self.student_number else f"Öğrenci ID: {self.student_id}"
    course_info = self.course_code if self.course_code else f"Ders ID: {self.course_id}"
    return f"{student_info} -> {course_info}"
```

---

## Student ve StudentCourse Model İlişkileri

### Veritabanı Şeması

```sql
-- Students tablosu
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    student_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    year INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student Courses tablosu
CREATE TABLE IF NOT EXISTS student_courses (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    semester VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id)
);
```

### İlişki Diyagramı

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────┐
│    students     │       │ student_courses  │       │   courses   │
├─────────────────┤       ├──────────────────┤       ├─────────────┤
│ id (PK)         │◄──────│ student_id (FK)  │───────►│ id (PK)     │
│ student_number  │       │ course_id (FK)   │       │ code        │
│ first_name      │       │ semester         │       │ name        │
│ last_name       │       │ is_active        │       │ department  │
│ email           │       └──────────────────┘       │ year        │
│ department_id   │                                   │ semester    │
│ year            │                                   └─────────────┘
│ is_active       │
└─────────────────┘
```

### Çakışma Kontrolü Kullanımı

Öğrenci bazlı çakışma kontrolü için bu ilişki kullanılır:

```python
# Ders A'nın öğrenci kümesi
students_A = {101, 102, 103, 104}

# Ders B'nin öğrenci kümesi
students_B = {103, 104, 105, 106}

# Kesişim kümesi
intersection = students_A & students_B  # {103, 104}

if intersection:
    # Çakışma var!
    print(f"Ortak öğrenci sayısı: {len(intersection)}")
```

### Öğrenci Import Süreci

1. **Excel Dosyası**: `exceller/SınıfListesi[BLM111].xls`
2. **StudentImporter**: Excel'den veriyi okur
3. **StudentRepository**: Öğrencileri kaydeder (UPSERT)
4. **StudentCourseRepository**: Öğrenci-ders ilişkilerini kaydeder

```python
from src.utils.student_importer import StudentImporter

importer = StudentImporter()
result = importer.import_from_excel(
    "exceller/SınıfListesi[BLM111].xls",
    course_id=1,
    semester="2024-2025 Güz"
)
# result.students_imported
# result.student_courses_created
```


**Dosya**: [`src/models/student.py`](../src/models/student.py:1)

### Sınıf Yapısı

```python
@dataclass
class StudentCourse:
    id: Optional[int] = None
    student_id: Optional[int] = None
    course_id: Optional[int] = None
    semester: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    # Join sonucu eklenen alanlar
    student_number: Optional[str] = None
    student_name: Optional[str] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None
```

### Özellikler

| Özellik | Tip | Varsayılan | Açıklama |
|---------|-----|------------|----------|
| `id` | Optional[int] | None | Benzersiz kimlik |
| `student_id` | Optional[int] | None | Öğrenci FK |
| `course_id` | Optional[int] | None | Ders FK |
| `semester` | Optional[str] | None | Dönem bilgisi |
| `is_active` | bool | True | Aktif mi? |
| `student_number` | Optional[str] | None | Join ile gelen |
| `student_name` | Optional[str] | None | Join ile gelen |
| `course_code` | Optional[str] | None | Join ile gelen |
| `course_name` | Optional[str] | None | Join ile gelen |

### Önemli Notlar

Bu model, **öğrenci bazlı çakışma kontrolü** için kullanılır. İki ders arasındaki çakışma, öğrenci kümelerinin kesişimi ile tespit edilir:

```python
# Örnek çakışma kontrolü mantığı
students_course_A = {101, 102, 103, 104}
students_course_B = {103, 104, 105, 106}
intersection = students_course_A & students_course_B  # {103, 104}

if intersection:
    # Çakışma var! Bu iki ders aynı saatte sınav olamaz
    print(f"Ortak öğrenci sayısı: {len(intersection)}")
```

---

## ExamSchedule Model

**Dosya**: [`src/models/exam_schedule.py`](../src/models/exam_schedule.py:1)

### Sınıf Yapısı

```python
@dataclass
class ExamSchedule:
    id: Optional[int] = None
    course_id: Optional[int] = None
    classroom_id: Optional[int] = None
    exam_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    exam_type: str = "final"
    status: str = "planned"
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Join sonucu eklenen alanlar
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    classroom_name: Optional[str] = None
    faculty_name: Optional[str] = None
    lecturer_name: Optional[str] = None
    department_name: Optional[str] = None
    student_count: Optional[int] = None
```

### Özellikler

| Özellik | Tip | Varsayılan | Açıklama |
|---------|-----|------------|----------|
| `id` | Optional[int] | None | Benzersiz kimlik |
| `course_id` | Optional[int] | None | Ders FK |
| `classroom_id` | Optional[int] | None | Derslik FK |
| `exam_date` | Optional[date] | None | Sınav tarihi |
| `start_time` | Optional[time] | None | Başlangıç saati |
| `end_time` | Optional[time] | None | Bitiş saati |
| `exam_type` | str | "final" | Sınav türü |
| `status` | str | "planned" | Durum |
| `notes` | Optional[str] | None | Notlar |

### Durum Değerleri

- `planned`: Planlandı
- `confirmed`: Onaylandı
- `cancelled`: İptal edildi

### Display Metodu

```python
def __str__(self) -> str:
    return f"{self.course_code} - {self.exam_date} {self.start_time}"
```

### ExamSupervisor Sınıfı

Sınav gözetmen ilişkisi için:

```python
@dataclass
class ExamSupervisor:
    id: Optional[int] = None
    exam_schedule_id: Optional[int] = None
    lecturer_id: Optional[int] = None
    is_chief: bool = False  # Baş gözetmen mi?
    created_at: Optional[datetime] = None
    
    lecturer_name: Optional[str] = None
```

---

## Model İlişkileri

### ER Diagram (Metin Temsili)

```
┌─────────────┐
│  faculties  │
│─────────────│
│ id (PK)     │───┐
│ name        │   │
│ code        │   │ 1
│ dean_name   │   │
└─────────────┘   │
                  │
                  │ N
        ┌─────────▼─────────┐
        │   departments     │
        │───────────────────│
        │ id (PK)           │───┐
        │ faculty_id (FK)   │   │
        │ name              │   │ 1
        │ code              │   │
        │ head_name         │   │
        └───────────────────┘   │
                                │
                ┌───────────────┼───────────────┐
                │ N             │ N             │ N
        ┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
        │  lecturers   │ │  courses   │ │ classrooms │
        │──────────────│ │────────────│ │────────────│
        │ id (PK)      │ │ id (PK)    │ │ id (PK)    │
        │ dept_id (FK) │ │ dept_id(FK)│ │ faculty_id │
        │ first_name   │ │ lecturer_id│ │ name       │
        │ last_name    │ │ code       │ │ capacity   │
        │ title        │ │ year       │ │ is_suitable│
        │ email        │ │ semester   │ │            │
        │ available_days││ has_exam   │ │            │
        └──────────────┘ └──────┬─────┘ └─────┬──────┘
                                │               │
                                │               │
                        ┌───────▼───────────────▼───────┐
                        │       exam_schedule          │
                        │───────────────────────────────│
                        │ id (PK)                      │
                        │ course_id (FK)               │
                        │ classroom_id (FK)            │
                        │ exam_date                    │
                        │ start_time                   │
                        │ end_time                     │
                        │ exam_type                    │
                        │ status                       │
                        └───────────────────────────────┘
```

### İlişki Kuralları

| Tablo | İlişki | Referans Tablo | Kural |
|-------|--------|----------------|-------|
| departments | faculty_id → | faculties | ON DELETE CASCADE |
| classrooms | faculty_id → | faculties | ON DELETE SET NULL |
| lecturers | department_id → | departments | ON DELETE SET NULL |
| courses | department_id → | departments | ON DELETE SET NULL |
| courses | lecturer_id → | lecturers | ON DELETE SET NULL |
| exam_schedule | course_id → | courses | ON DELETE CASCADE |
| exam_schedule | classroom_id → | classrooms | ON DELETE CASCADE |
| users | department_id → | departments | ON DELETE SET NULL |

### Unique Constraints

| Tablo | Kolon(lar) | Açıklama |
|-------|------------|----------|
| faculties | code | Fakülte kodu benzersiz |
| departments | code | Bölüm kodu benzersiz |
| lecturers | email | E-posta benzersiz |
| courses | code | Ders kodu benzersiz |
| users | username | Kullanıcı adı benzersiz |
| users | email | E-posta benzersiz |
| exam_schedule | (classroom_id, exam_date, start_time) | Derslik-zaman benzersiz |

---

## Olası Hatalar

### 1. Serileştirme Hataları

#### Hata: JSON Serialization
```python
# datetime objeleri JSON'a serileştirilemez
json.dumps(user.to_dict())  # ❌ TypeError

# Çözüm: datetime string'e çevrilmeli
```

#### Hata: Listesi Kolonlar
```python
# available_days TEXT[] PostgreSQL'de array
# from_dict'te string olarak gelebilir
# Çözüm: Lecturer.from_dict bu durumu ele alıyor
```

### 2. Tip Uyuşmazlıkları

#### Hata: None vs Boş String
```python
# Veritabanında NULL, Python'da "" olabilir
course.description = ""  # NULL yerine
course.description = None  # Doğrusu
```

#### Hata: Int vs String
```python
# Formdan gelen veriler string olarak gelebilir
course.year = "1"  # ❌
course.year = 1    # ✅
```

### 3. İlişki Hataları

#### Hata: FK Null Kontrolü
```python
# department_id None olan bir departemente erişilmeye çalışılırsa
dept_name = course.department_name  # None olabilir
if dept_name:
    print(dept_name)
```

#### Hata: Silme Cascade
```python
# Faculty silindiğinde departments da silinir (CASCADE)
# Ama classrooms'da faculty_id NULL olur (SET NULL)
# Bu beklenmeden NULL reference yaratabilir
```

### 4. Validasyon Eksiklikleri

#### Email Validasyonu
```python
# Mevcut: Yok
# Öneri:
import re
def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

#### Kod Formatı Validasyonu
```python
# Bölüm kodları 2-3 karakter olmalı
if len(department.code) > 3:
    raise ValueError("Bölüm kodu en fazla 3 karakter olabilir")
```

### 5. Tarih/Zaman Hataları

#### Hata: Date vs Datetime
```python
# exam_schedule exam_date DATE tipinde
# Ama Python'da datetime gelebilir
# Çözüm: Tarih extract edilmalı
```

#### Hata: Time String
```python
# "09:00" string, time objesi gerekli
from datetime import time
start_time = time.fromisoformat("09:00")  # Python 3.7+
```

### 6. Array Kolon Hataları

#### Hata: PostgreSQL Array → Python List
```python
# Veritabanı: '{Pazartesi,Salı}'
# Python'da parse gerekli
available_days = data.get('available_days', [])
if isinstance(available_days, str):
    available_days = available_days.strip('{}').split(',')
```

---

## Kullanım Örnekleri

### Model Oluşturma

```python
from src.models.user import User
from src.models.course import Course
from datetime import datetime

# Kullanıcı oluştur
user = User(
    username="admin",
    first_name="Admin",
    last_name="User",
    role="admin"
)
user.set_password("admin123")

# Ders oluştur
course = Course(
    code="BM13101",
    name="Programlamaya Giriş",
    credit=4,
    year=1,
    semester=1,
    student_count=60,
    exam_duration=90
)
```

### Model Dönüştürme

```python
# Dict → Model
user = User.from_dict({
    'id': 1,
    'username': 'admin',
    'role': 'admin',
    'first_name': 'Admin',
    'last_name': 'User'
})

# Model → Dict
data = user.to_dict()
```

### Model İlişkileri

```python
# Ders ve bağlı veriler
course = Course.from_dict({
    'id': 1,
    'code': 'BM13101',
    'name': 'Programlamaya Giriş',
    'department_name': 'Bilgisayar Mühendisliği',  # Join
    'lecturer_name': 'Prof. Dr. Ayşe Yılmaz',        # Join
    'faculty_name': 'Mühendislik Fakültesi'         # Join
})
```

---

## Öneriler

1. **Pydantic Kullanımı**: Dataclass yerine Pydantic kullanarak otomatik validasyon
2. **Enum Kullanımı**: Rol, durum sabitleri için enum
3. **Mixin Sınıflar**: Ortak metodlar için base model
4. **Type Hints**: Daha spesifik type hints (örn: `Literal["admin", "bolum_yetkilisi"]`)
5. **Validasyon Dekoratörleri**: `@validates` ile alan validasyonu
