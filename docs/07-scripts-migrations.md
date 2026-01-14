# Veri İçe Aktarma ve Kurulum

Bu doküman, projede veri nasıl içe aktarılacağını açıklar. Proje mock/test verileri kullanmaz, tüm veriler gerçek Excel dosyalarından gelir.

## Veritabanı Kurulumu

### Temel Kurulum

```bash
python database/core/setup_db.py
```

Bu komut şunları yapar:
1. `universite_sinav_db` veritabanını oluşturur (yoksa)
2. Tüm tabloları oluşturur (faculties, departments, classrooms, lecturers, courses, exam_schedule, users, students, student_courses)
3. Gerekli indeksleri oluşturur
4. `updated_at` trigger'larını ekler

---

## Öğrenci Verisi İçe Aktarma

### Excel Dosya Formatı

`exceller/` klasöründeki dosyalar şu formatta olmalıdır:

| Öğrenci No | Ad | Soyad | E-posta | Bölüm | Sınıf |
|-----------|----|-------|--------|-------|-------|
| 2021001 | Ahmet | Yılmaz | ahmet@example.com | Bilgisayar Müh. | 1 |
| 2021002 | Ayşe | Demir | ayse@example.com | Yazılım Müh. | 2 |

### Kullanım

#### Tek Dosya Import

```python
from src.services.student_import_service import StudentImportService

service = StudentImportService()

result = service.import_from_excel(
    file_path="exceller/SınıfListesi[BLM111].xls",
    course_id=1,
    semester="2024-2025 Güz"
)

print(f"{result.students_imported} öğrenci eklendi")
```

#### Klasör Import (Tüm Excel Dosyaları)

```python
from src.services.student_import_service import StudentImportService

service = StudentImportService()

results = service.import_from_excel_directory(
    directory_path="exceller/",
    semester="2024-2025 Güz"
)

# Özet
summary = service.get_import_summary(results)
print(f"Toplam {summary['total_students_imported']} öğrenci import edildi")
```

### Desteklenen Ders Kodları

`exceller/` klasöründeki mevcut dosyalar:

| Dosya Adı | Ders Kodu |
|-----------|-----------|
| SınıfListesi[BLM111].xls | BLM111 |
| SınıfListesi[BLM328].xls | BLM328 |
| SınıfListesi[BLM331].xls | BLM331 |
| SınıfListesi[MAT110] (3).xls | MAT110 |
| SınıfListesi[MAT110] (4).xls | MAT110 |
| SınıfListesi[MAT211] (1).xls | MAT211 |
| SınıfListesi[MAT213] (4).xls | MAT213 |
| SınıfListesi[MAT220] (2).xls | MAT220 |
| SınıfListesi[SEC908].xls | SEC908 |
| SınıfListesi[YZM119].xls | YZM119 |
| SınıfListesi[YZM326].xls | YZM326 |
| SınıfListesi[YZM329].xls | YZM329 |
| SınıfListesi[YZM332].xls | YZM332 |

---

## Derslik Yakınlık Verisi

Derslik yakınlık bilgileri [`ClassroomProximityLoader`](../src/utils/classroom_proximity_loader.py) tarafından yönetilir.

### Veri Kaynağı

1. **Öncelik:** `exceller/Derslik Yakınlık (1).xlsx` (varsa)
2. **Fallback:** [`_load_manual_data()`](../src/utils/classroom_proximity_loader.py:200) içindeki tanımlı veriler

### Manuel Veri Yapısı

```python
# Format: (BLOK, DERSLİK, YAKIN DERSLİKLER)
("M", "M101", "S101,M201,M301,S201,S202"),
("S", "S101", "M101,S201,S202,M201,M301"),
("D", "D101", "D102,D103,D104,D201,D202"),
# ... daha fazlası
```

### Kullanım

```python
from src.utils.classroom_proximity_loader import get_proximity_loader

loader = get_proximity_loader()

# Komşuları al
neighbors = loader.get_neighbors("M101")

# Blok bilgisini al
block = loader.get_block("M101")

# İki derslik yakın mı?
is_near = loader.are_neighbors("M101", "S101")
```

---

## İlk Kurulum Adımları

1. **Veritabanını oluştur:**
   ```bash
   python database/core/setup_db.py
   ```

2. **Admin kullanıcısı oluştur** (manuel olarak):
   ```sql
   INSERT INTO users (username, password_hash, email, first_name, last_name, role)
   VALUES ('admin', 'admin123_hash', 'admin@example.com', 'Admin', 'User', 'admin');
   ```

3. **Fakülte ve bölüm verilerini ekle** (manuel olarak veya GUI üzerinden)

4. **Derslik verilerini ekle** (manuel olarak veya GUI üzerinden)

5. **Ders verilerini ekle** (manuel olarak veya GUI üzerinden)

6. **Öğrenci verilerini Excel'den import et:**
   ```python
   from src.services.student_import_service import StudentImportService
   service = StudentImportService()
   results = service.import_from_excel_directory("exceller/", "2024-2025 Güz")
   ```
