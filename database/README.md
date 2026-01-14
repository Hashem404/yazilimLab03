# Database Klasörü Yapısı

Bu klasör, veritabanı ile ilgili tüm kurulum ve bağlantı dosyalarını içerir.

## 📁 core/
Ana kurulum dosyaları:
- `setup_db.py` - Veritabanı ve tüm tabloları oluşturur
- `connection.py` - Veritabanı bağlantı yönetimi (connection pooling)

---

## Kullanım

### Veritabanı Kurulumu

```bash
python database/core/setup_db.py
```

Bu komut şunları yapar:
1. `universite_sinav_db` veritabanını oluşturur (yoksa)
2. Tüm tabloları oluşturur:
   - `faculties` - Fakülteler
   - `departments` - Bölümler
   - `classrooms` - Derslikler (room_type desteği ile)
   - `lecturers` - Öğretim Üyeleri
   - `courses` - Dersler (required_room_type desteği ile)
   - `exam_schedule` - Sınav Programı
   - `users` - Kullanıcılar
   - `students` - Öğrenciler
   - `student_courses` - Öğrenci-Ders İlişkileri
3. Gerekli indeksleri oluşturur
4. `updated_at` trigger'larını ekler

### Veritabanı Bağlantısı

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

## Gerçek Veri ile Çalışma

Bu proje mock/test verileri kullanmaz. Gerçek öğrenci verileri `exceller/` klasöründeki Excel dosyalarından import edilir.

### Öğrenci Import

```python
from src.services.student_import_service import StudentImportService

service = StudentImportService()

# Tek dosya import
result = service.import_from_excel(
    "exceller/SınıfListesi[BLM111].xls",
    course_id=1,
    semester="2024-2025 Güz"
)

# Klasör import (tüm Excel dosyaları)
results = service.import_from_excel_directory(
    "exceller/",
    semester="2024-2025 Güz"
)
```

---

## Tablo Yapısı

### students
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | SERIAL | Primary Key |
| student_number | VARCHAR(20) | Öğrenci No (Unique) |
| first_name | VARCHAR(50) | Ad |
| last_name | VARCHAR(50) | Soyad |
| email | VARCHAR(100) | E-posta |
| department_id | INTEGER | Bölüm FK |
| year | INTEGER | Sınıf (1-4) |
| is_active | BOOLEAN | Aktif mi? |
| created_at | TIMESTAMP | Oluşturulma Tarihi |
| updated_at | TIMESTAMP | Güncelleme Tarihi |

### student_courses
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | SERIAL | Primary Key |
| student_id | INTEGER | Öğrenci FK |
| course_id | INTEGER | Ders FK |
| semester | VARCHAR(50) | Dönem |
| is_active | BOOLEAN | Aktif mi? |
| created_at | TIMESTAMP | Oluşturulma Tarihi |

---

## Derslik Tipleri

Derslikler `room_type` alanına göre kategorize edilir:
- `STANDART` - Standart Derslik
- `LAB` - Bilgisayar Laboratuvarı
- `OFIS` - Ofis
- `DEKANLIK` - Dekanlık
- `BILGISALONU` - Bilgisayar Salonu
- `KONFERANS` - Konferans Salonu

Dersler `required_room_type` alanı ile gerektirdikleri oda tipini belirtebilir (`ANY` = herhangi bir derslik).
