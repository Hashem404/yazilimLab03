# Başlangıç Rehberi - Adım Adım Kurulum

Bu rehber, projeyi sıfırdan kurmanıza ve çalıştırmanıza yardımcı olur.

## Ön Koşullar

1. **PostgreSQL** kurulu olmalı (v14 veya üzeri önerilir)
2. **Python 3.8+** kurulu olmalı
3. PostgreSQL servisi çalışıyor olmalı

## Adım 1: Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

Bu komut şunları yükler:
- `psycopg2-binary` - PostgreSQL bağlantısı
- `xlrd` - .xls dosya okuma
- `openpyxl` - .xlsx dosya okuma
- `bcrypt` - Şifre hashleme
- `python-dotenv` - Ortam değişkenleri
- `pytest` - Test

## Adım 2: Veritabanını Oluşturun

```bash
python database/core/setup_db.py
```

Bu komut:
- `universite_sinav_db` veritabanını oluşturur
- Tüm tabloları oluşturur
- Indeksleri ve trigger'ları kurar

## Adım 3: Varsayılan Kullanıcıları Oluşturun

```bash
python database/scripts/create_default_users.py
```

**Varsayılan Giriş Bilgileri:**

| Kullanıcı Adı | Şifre | Rol |
|--------------|------|-----|
| `admin` | admin123 | Sistem Yöneticisi (tam yetki) |
| `bolum_yetkilisi` | admin123 | Bölüm Yetkilisi |
| `hoca` | admin123 | Öğretim Üyesi |
| `ogrenci` | admin123 | Öğrenci |
| `viewer` | admin123 | Sadece Görüntüleme |

## Adım 4: Uygulamayı Başlatın

```bash
python src/main.py
```

Uygulama açıldığında giriş ekranı göreceksiniz. Varsayılan kullanıcılarla giriş yapabilirsiniz.

---

# Mock Data Kullanmadan Sistemi Çalıştırma

Bu proje **mock data kullanmaz**. Gerçek üniversite verileriyle çalışmak üzere tasarlanmıştır.

## Veri Kaynakları

### 1. Gerçek Veriler (Korumalı - Temizlenmez)
Bu veriler manuel olarak eklenir veya import edilir ve sistemde kalır:

| Tablo | Veri Kaynağı |
|-------|-------------|
| `faculties` | GUI üzerinden manuel ekleme |
| `departments` | GUI üzerinden manuel ekleme |
| `classrooms` | GUI üzerinden manuel ekleme |
| `lecturers` | GUI üzerinden manuel ekleme |
| `courses` | GUI üzerinden manuel ekleme |
| `users` | `create_default_users.py` scripti veya GUI |

### 2. Öğrenci Verileri (Excel'den - Temizlenebilir)
Bu veriler Excel'den gelir ve istenirse temizlenebilir:

| Tablo | Veri Kaynağı | Temizleme |
|-------|-------------|----------|
| `students` | `exceller/` klasöründeki .xls dosyaları | `clear_student_data.py` |
| `student_courses` | Excel import sırasında otomatik oluşturulur | `clear_student_data.py` |

---

# İlk Verileri Ekleme (Örnek Senaryo)

## 1. Fakülte Ekleme
```sql
INSERT INTO faculties (name, code, dean_name) VALUES
('Mühendislik Fakültesi', 'MUF', 'Prof. Dr. Ahmet Yılmaz'),
('Fen Edebiyat Fakültesi', 'FEF', 'Prof. Dr. Ayşe Demir');
```

## 2. Bölüm Ekleme
```sql
INSERT INTO departments (name, code, faculty_id) VALUES
('Bilgisayar Mühendisliği', 'BLM', 1),
('Matematik Mühendisliği', 'MAT', 1),
('Yazılım Mühendisliği', 'YZM', 1);
```

## 3. Derslik Ekleme
```sql
INSERT INTO classrooms (name, building, capacity, floor, room_type, faculty_id) VALUES
('M101', 'Mühendislik A Blok', 60, 1, 'STANDART', 1),
('M102', 'Mühendislik A Blok', 40, 1, 'STANDART', 1),
('LAB101', 'Mühendislik B Blok', 30, 0, 'LAB', 1);
```

## 4. Öğretim Üyesi Ekleme
```sql
INSERT INTO lecturers (first_name, last_name, title, email, department_id) VALUES
('Ahmet', 'Yılmaz', 'Dr. Öğr. Üyesi', 'ahmet.yilmaz@uni.edu.tr', 1),
('Ayşe', 'Demir', 'Prof. Dr.', 'ayse.demir@uni.edu.tr', 1);
```

## 5. Ders Ekleme
```sql
INSERT INTO courses (name, code, department_id, lecturer_id, student_count, exam_duration, year) VALUES
('Programlamaya Giriş', 'BLM101', 1, 1, 60, 60, 1),
('Veri Yapıları', 'BLM102', 1, 1, 50, 90, 2),
('Analiz I', 'MAT101', 2, 2, 80, 120, 1);
```

---

# Öğrenci Verisi İçe Aktarma

## Tek Dosya İçe Aktarma

```python
from src.services.student_import_service import StudentImportService

service = StudentImportService()

result = service.import_from_excel(
    "exceller/SınıfListesi[BLM111].xls",
    course_code="BLM111",  # veya course_id=1
    semester="2024-2025 Güz"
)

print(result.message)
```

## Tüm Excel Dosyalarını İçe Aktarma

```python
from src.services.student_import_service import StudentImportService

service = StudentImportService()
results = service.import_from_excel_directory(
    "exceller/",
    semester="2024-2025 Güz"
)

for filename, result in results.items():
    print(f"{filename}: {result.message}")
```

---

# Sınav Programı Oluşturma

Uygulamayı başlatıp `admin` kullanıcısıyla giriş yaptıktan sonra:

1. **Dashboard** ekranında "Otomatik Sınav Planla" butonuna tıklayın
2. Tarih aralığını seçin (örn: 2025-01-20 ile 2025-01-31 arası)
3. Departman seçin (tüm departmanlar için boş bırakın)
4. "Planla" butonuna tıklayın

veya Python kodu ile:

```python
from src.services.scheduler_service import SchedulerService

scheduler = SchedulerService()

result = scheduler.generate_schedule(
    start_date="2025-01-20",
    end_date="2025-01-31",
    exam_type="final",
    clear_existing=True
)

print(result['message'])
print(f"Planlanan: {result['scheduled_count']}")
print(f"Planlanamayan: {result['failed_count']}")
```

---

# Öğrenci Verilerini Temizleme

Excel'den import edilen öğrenci verilerini temizlemek için:

```bash
python database/scripts/clear_student_data.py
```

Bu komut **sadece** `students` ve `student_courses` tablolarını temizler.
Diğer tüm veriler (fakülteler, bölümler, dersler, vb.) korunur.

---

# Testleri Çalıştırma

```bash
python tests.py
```

Testler veritabanı bağlantısı gerektirmez, mock verilerle çalışır.

---

# Sorun Giderme

## PostgreSQL Bağlantı Hatası

```
psycopg2.OperationalError: could not connect to server
```

**Çözüm:** PostgreSQL servisini başlatın
```bash
# Linux/WSL
sudo service postgresql start

# Windows
# Services'de PostgreSQL servisini başlatın
```

## xlrd Modül Hatası

```
ModuleNotFoundError: No module named 'xlrd'
```

**Çözüm:** requirements.txt'den yükleyin
```bash
pip install -r requirements.txt
```

## Giriş Yapamıyorum

**Çözüm:** Varsayılan kullanıcıları oluşturun
```bash
python database/scripts/create_default_users.py
```

Kullanıcı adı: `admin`
Şifre: `admin123`

## Veritabanı Boş Görünüyor

**Çözüm 1:** Önce tabloları oluşturun
```bash
python database/core/setup_db.py
```

**Çözüm 2:** Örnek veriler ekleyin (SQL ile veya GUI'den)

---

# Proje Yapısı

```
yazilimLab03/
├── database/
│   ├── core/
│   │   ├── connection.py      # Bağlantı havuzu
│   │   └── setup_db.py        # DB kurulum
│   └── scripts/
│       ├── create_default_users.py    # Kullanıcı oluşturma
│       └── clear_student_data.py      # Öğrenci temizleme
├── src/
│   ├── models/        # Veri modelleri
│   ├── repositories/  # Veritabanı erişimi
│   ├── services/      # İş mantığı
│   ├── views/         # Tkinter arayüz
│   └── utils/         # Yardımcı fonksiyonlar
├── exceller/          # Öğrenci Excel dosyaları
├── docs/              # Dokümantasyon
└── tests.py           # Test suite
```
