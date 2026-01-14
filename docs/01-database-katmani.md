# Database Katmanı Dokümantasyonu

Bu dokümantasyon, veritabanı katmanındaki temel bileşenleri açıklar.

## İçindekiler
- [connection.py Analizi](#connectionpy-analizi)
- [setup_db.py Analizi](#setup_dbpy-analizi)
- [Veritabanı Tablo Yapısı](#veritaban-tablo-yaps)

---

## connection.py Analizi

**Dosya Konumu**: [`database/core/connection.py`](../database/core/connection.py)

### Amaç
PostgreSQL veritabanı bağlantı yönetimi sağlar. Connection pooling (bağlantı havuzu) kullanır ve Singleton pattern uygular.

### Sınıflar

#### `DatabaseConfig`
Veritabanı konfigürasyonunu yönetir. Ortam değişkenlerinden veya varsayılan değerlerden okur.

| Özellik | Tip | Açıklama |
|---------|-----|----------|
| `host` | str | Veritabanı sunucusu (varsayılan: localhost) |
| `port` | str | Port numarası (varsayılan: 5432) |
| `database` | str | Veritabanı adı (varsayılan: universite_sinav_db) |
| `user` | str | Kullanıcı adı (varsayılan: postgres) |
| `password` | str | Şifre (varsayılan: postgres) |

**Metotlar**:
- `get_connection_string()`: Bağlantı string'i döndürür
- `get_connection_dict()`: Bağlantı parametrelerini dict olarak döndürür

#### `DatabaseConnection`
Singleton pattern ile tek bir bağlantı havuzu örneği yönetir.

**Özellikler**:
- `_instance`: Singleton instance
- `_pool`: psycopg2 SimpleConnectionPool (min: 1, max: 10)

**Metotlar**:

| Metot | Açıklama |
|-------|----------|
| `get_connection()` | Havuzdan bir bağlantı alır |
| `release_connection(conn)` | Bağlantıyı havuza geri bırakır |
| `close_all()` | Tüm bağlantıları kapatır |

### Global Fonksiyonlar

```python
get_connection()      # Yeni bağlantı döndürür
release_connection(conn)  # Bağlantıyı serbest bırakır
close_all_connections()    # Tüm bağlantıları kapatır
```

### Olası Hatalar

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| **OperationalError** | Veritabanı sunucusu çalışmıyor | PostgreSQL servisini başlatın |
| **InterfaceError** | Bağlantı havuzu tükenmiş | `maxconn` değerini artırın |
| **ProgrammingError** | Yanlış SQL sözdizimi | SQL sorgularını kontrol edin |
| **AuthenticationError** | Yanlış kimlik bilgileri | `.env` dosyasını kontrol edin |

### Kod Örneği
```python
from database.core.connection import get_connection, release_connection

conn = get_connection()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
finally:
    release_connection(conn)
```

---

## setup_db.py Analizi

**Dosya Konumu**: [`database/core/setup_db.py`](../database/core/setup_db.py)

### Amaç
Veritabanını ve tabloları oluşturur. Gerekli indeksleri ve trigger'ları kurar.

### Konfigürasyon

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "password": "123",  # ⚠️ Güvenlik sorunu
}

TARGET_DB_NAME = "universite_sinav_db"
```

### Fonksiyonlar

#### `create_database_if_not_exists()`
Veritabanı yoksa oluşturur.

**Adımlar**:
1. `postgres` veritabanına bağlanır
2. Hedef veritabanının varlığını kontrol eder
3. Yoksa `CREATE DATABASE` komutunu çalıştırır

#### `create_updated_at_trigger(cur)`
Tüm tablolar için `updated_at` kolonunu otomatik güncelleyen trigger'ı oluşturur.

**Trigger Fonksiyonu**:
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';
```

**Trigger'lar eklenen tablolar**:
- faculties
- departments
- classrooms
- lecturers
- courses
- exam_schedule
- users

#### `create_tables()`
Tüm tabloları, indeksleri ve trigger'ları oluşturur.

### Tablo Yapıları

#### faculties
```sql
CREATE TABLE faculties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE,
    dean_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### departments
```sql
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE,
    faculty_id INTEGER REFERENCES faculties(id) ON DELETE CASCADE,
    head_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### classrooms
```sql
CREATE TABLE classrooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    building VARCHAR(50) DEFAULT '',
    capacity INTEGER NOT NULL,
    floor INTEGER DEFAULT 0,
    exam_capacity INTEGER,
    has_projector BOOLEAN DEFAULT FALSE,
    has_computer BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_suitable BOOLEAN DEFAULT TRUE,
    faculty_id INTEGER REFERENCES faculties(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### lecturers
```sql
CREATE TABLE lecturers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    title VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    available_days TEXT[] DEFAULT '{Pazartesi,Salı,Çarşamba,Perşembe,Cuma}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### courses
```sql
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    lecturer_id INTEGER REFERENCES lecturers(id) ON DELETE SET NULL,
    student_count INTEGER NOT NULL,
    exam_duration INTEGER CHECK (exam_duration IN (30, 60, 90, 120)),
    exam_type VARCHAR(50),
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    code VARCHAR(20) UNIQUE,
    year INTEGER,
    semester INTEGER,
    period INTEGER,
    theory_hours INTEGER DEFAULT 0,
    lab_hours INTEGER DEFAULT 0,
    course_type VARCHAR(30) DEFAULT 'Zorunlu',
    description TEXT,
    lecturer_count INTEGER DEFAULT 1,
    has_exam BOOLEAN DEFAULT TRUE,
    credit INTEGER DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### exam_schedule
```sql
CREATE TABLE exam_schedule (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    classroom_id INTEGER REFERENCES classrooms(id) ON DELETE CASCADE,
    exam_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    exam_type VARCHAR(20) DEFAULT 'final',
    status VARCHAR(20) DEFAULT 'planned',
    notes TEXT,
    building VARCHAR(50),
    classroom_name VARCHAR(50),
    course_code VARCHAR(20),
    course_name VARCHAR(100),
    lecturer_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_classroom_time UNIQUE (classroom_id, exam_date, start_time)
)
```

#### users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'bolum_yetkilisi', 'hoca', 'ogrenci', 'editor', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### students ⭐ (Yeni - Migration 016)
```sql
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
)
```

#### student_courses ⭐ (Yeni - Migration 016)
```sql
CREATE TABLE IF NOT EXISTS student_courses (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    semester VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id)
)
```

### İndeksler

```sql
-- Fakülteler
CREATE INDEX idx_faculties_code ON faculties(code);

-- Bölümler
CREATE INDEX idx_departments_faculty_id ON departments(faculty_id);

-- Derslikler
CREATE INDEX idx_classrooms_faculty_id ON classrooms(faculty_id);
CREATE INDEX idx_classrooms_suitable ON classrooms(is_suitable);

-- Öğretim Üyeleri
CREATE INDEX idx_lecturers_department_id ON lecturers(department_id);
CREATE INDEX idx_lecturers_email ON lecturers(email);

-- Dersler
CREATE INDEX idx_courses_code ON courses(code);
CREATE INDEX idx_courses_department_id ON courses(department_id);
CREATE INDEX idx_courses_lecturer_id ON courses(lecturer_id);
CREATE INDEX idx_courses_department_lecturer ON courses(department_id, lecturer_id);

-- Sınav Programı
CREATE INDEX idx_exam_schedule_date ON exam_schedule(exam_date);
CREATE INDEX idx_exam_schedule_course_id ON exam_schedule(course_id);
CREATE INDEX idx_exam_schedule_classroom_id ON exam_schedule(classroom_id);

-- Kullanıcılar
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_department_id ON users(department_id);

-- Öğrenciler (Yeni - Migration 016)
CREATE INDEX IF NOT EXISTS idx_students_student_number ON students(student_number);
CREATE INDEX IF NOT EXISTS idx_students_department_id ON students(department_id);
CREATE INDEX IF NOT EXISTS idx_students_year ON students(year);
CREATE INDEX IF NOT EXISTS idx_students_active ON students(is_active);

-- Öğrenci-Ders İlişkileri (Yeni - Migration 016)
CREATE INDEX IF NOT EXISTS idx_student_courses_student_id ON student_courses(student_id);
CREATE INDEX IF NOT EXISTS idx_student_courses_course_id ON student_courses(course_id);
CREATE INDEX IF NOT EXISTS idx_student_courses_active ON student_courses(is_active);
```

### Olası Hatalar

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| **DatabaseExists** | Veritabanı zaten var | Fonksiyon kontrol eder ve geçer |
| **PermissionDenied** | Yetersiz izin | PostgreSQL kullanıcısına DB oluşturma izni verin |
| **DuplicateTable** | Tablo zaten var | `IF NOT EXISTS` kullanılmış, hata vermez |
| **ForeignKeyViolation** | Yanlış sıralama | Cascade delete için doğru sıralama |
| **DuplicateColumn** | Kolon zaten var | `IF NOT EXISTS` kontrolü ekleyin |

### Kullanım
```bash
# Veritabanını sıfırdan oluştur
cd database/core
python setup_db.py
```

---

## Veritabanı Tablo Yapısı

### Bağlantı Hataları

```python
# Hata: could not connect to server
psycopg2.OperationalError: could not connect to server

# Çözüm:
# 1. PostgreSQL servisini başlat
sudo service postgresql start

# 2. Bağlantı bilgilerini kontrol et
# .env dosyasını veya DB_CONFIG'u kontrol et
```

### Yetki Hataları

```python
# Hata: permission denied for database
psycopg2.InsufficientPrivilege

# Çözüm:
# PostgreSQL kullanıcısına gerekli yetkileri ver
GRANT ALL PRIVILEGES ON DATABASE universite_sinav_db TO postgres;
```

### Kilitlenme Sorunları

```python
# Hata: deadlock detected
psycopg2.extensions.TransactionRollbackError

# Çözüm:
# 1. Daha kısa transaction'lar kullan
# 2. Tabloları her zaman aynı sırada eriş
# 3. Yeterli timeout değeri ayarla
```

### Performans Önerileri

1. **Connection Pool Ayarları**:
   ```python
   # Mevcut: minconn=1, maxconn=10
   # Öneri: minconn=5, maxconn=20 (yüksek trafik için)
   ```

2. **Sorgu Optimizasyonu**:
   - `EXPLAIN ANALYZE` kullanarak yavaş sorguları tespit edin
   - JOIN sorgularında indeks kullanımını kontrol edin

3. **Backup Stratejisi**:
   ```bash
   pg_dump universite_sinav_db > backup.sql
   ```

---

## Kaynaklar

- [PostgreSQL Dokümantasyonu](https://www.postgresql.org/docs/)
- [psycopg2 Dokümantasyonu](https://www.psycopg.org/docs/)
- [Faker Dokümantasyonu](https://faker.readthedocs.io/)
