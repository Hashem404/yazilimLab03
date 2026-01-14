# Üniversite Sınav Programı Sistemi - Genel Özet

## 1. Proje Genel Bakış

Bu proje, üniversite sınav programlarını otomatik olarak planlayan ve yöneten bir masaüstü uygulamasıdır. Sistem, fakülteler, bölümler, derslikler, öğretim üyeleri, öğrenciler ve dersler arasındaki ilişkileri yönetir ve çakışmasız bir sınav programı oluşturur.

### Temel Özellikler
- Otomatik sınav programı oluşturma (Greedy + Backtracking algoritması)
- Rol bazlı erişim kontrolü (Admin, Bölüm Yetkilisi, Hoca, Öğrenci)
- Tkinter tabanlı grafiksel arayüz
- PostgreSQL veritabanı entegrasyonu
- Excel raporlama özelliği
- **Öğrenci bazlı çakışma kontrolü** (Gerçek öğrenci listeleri üzerinden)
- **Öğrenci import** (Excel'den toplu öğrenci ekleme)
- **Derslik yakınlık grafiği** (Birleştirme için optimize edilmiş seçim)

## 2. Mimari Özeti

### Katmanlı Mimari
Proje, klasik n-tier mimari desenini takip eder:

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                     │
│   (Views - Tkinter Widgets, Controllers)                │
├─────────────────────────────────────────────────────────┤
│                    Business Logic Layer                 │
│              (Services, Validators)                     │
├─────────────────────────────────────────────────────────┤
│                   Data Access Layer                     │
│              (Repositories, Models)                     │
├─────────────────────────────────────────────────────────┤
│                    Database Layer                       │
│                 (PostgreSQL + psycopg2)                 │
└─────────────────────────────────────────────────────────┘
```

### Dizin Yapısı
```
yazilimLab03/
├── database/           # Veritabanı kurulum
│   └── core/          # Bağlantı, setup
├── src/
│   ├── config/        # Veritabanı konfigürasyonu
│   ├── controllers/   # View-Service köprüsü
│   ├── models/        # Veri modelleri (dataclass)
│   │   ├── student.py         # Öğrenci modeli
│   │   └── ...
│   ├── repositories/  # Veritabanı erişim katmanı
│   │   ├── student_repository.py    # Öğrenci repo
│   │   └── ...
│   ├── services/      # İş mantığı katmanı
│   │   ├── exam_schedule_service.py  # Öğrenci bazlı çakışma
│   │   ├── scheduler_service.py      # Otomatik planlama
│   │   └── student_import_service.py # Öğrenci import servisi
│   ├── utils/         # Yardımcı fonksiyonlar
│   │   ├── student_importer.py       # Excel'den öğrenci import
│   │   ├── classroom_proximity_loader.py  # Derslik yakınlık grafiği
│   │   └── ...
│   └── views/         # Tkinter arayüz bileşenleri
├── exceller/          # Excel veri dosyaları (gerçek öğrenci listeleri)
│   ├── SınıfListesi[BLM111].xls
│   ├── SınıfListesi[BLM328].xls
│   └── ... (toplam 13 dosya)
└── docs/              # Dokümantasyon (bu klasör)
```

## 3. Güçlü Yönler

### 3.1 Mimari Güçlü Yönler
- **Katmanlı Yapı**: Her katmanın sorumluluğu net ayrılmış
- **Repository Pattern**: Veritabanı erişimi soyutlanmış
- **Generic BaseRepository**: Tekrar eden kod minimize edilmiş
- **Dataclass Modeller**: Tip güvenliği ve serileştirme kolaylığı
- **Singleton Pattern**: Veritabanı bağlantı havuzu yönetimi

### 3.2 Algoritmik Güçlü Yönler
- **Öğrenci Bazlı Çakışma Kontrolü**: Gerçek öğrenci listeleri üzerinden kesişim kontrolü
- **Greedy + Backtracking**: Önce büyük grupları planlar, gerisini iteratif dener
- **Derslik Birleştirme**: Yeterli kapasite yoksa birden fazla derslik birleştirilebilir
- **Derslik Yakınlık Grafiği**: Birleştirme için optimize edilmiş derslik seçimi
- **Öğretim Üyesi Müsaitlik Kontrolü**: Haftanın günlerine göre müsaitlik kontrolü

### 3.2.1 Öğrenci Bazlı Çakışma Kontrolü

```python
# Ders A'nın öğrenci kümesi
students_A = {2021001, 2021002, 2021003, 2021004}

# Ders B'nin öğrenci kümesi
students_B = {2021003, 2021004, 2021005, 2021006}

# Kesişim kümesi
intersection = students_A & students_B  # {2021003, 2021004}

if intersection:
    # Çakışma var! Bu iki ders aynı saatte sınav olamaz
    print(f"Ortak öğrenci sayısı: {len(intersection)}")
```

### 3.3 UI/UX Güçlü Yönler
- **Rol Bazlı Menü**: Her kullanıcı rolüne uygun menü gösterilir
- **Temel CRUD Bileşeni**: Tekrar eden CRUD işlemleri için base sınıf
- **Responsive Tablo**: DataTable bileşeni ile scrollable veri gösterimi
- **Modal Dialog Form**: FormDialog bileşeni ile tutarlı form deneyimi

## 4. Zayıf Yönler ve Kritik Sorunlar

### 4.1 Güvenlik Sorunları
| Sorun | Öncelik | Açıklama |
|-------|---------|----------|
| **SHA256 Şifreleme** | 🔴 Kritik | SHA256 artık güvenli kabul edilmiyor, bcrypt/Argon2 kullanılmalı |
| **Plain SQL Sorgular** | 🟡 Orta | SQL Injection riski var, parametreli sorgular kullanılıyor ama tam değil |
| **Parola Ekranda Yazılı** | 🟡 Orta | `.env.example` dosyasında plain password var (`123`) |
| **Hardcoded Kimlik Bilgileri** | 🟡 Orta | `setup_db.py` içinde kullanıcı adı/şifre var |

### 4.2 Kod Kalitesi Sorunları
| Sorun | Öncelik | Açıklama |
|-------|---------|----------|
| **İstisna Yönetimi** | 🟡 Orta | Çoğu yerde `except Exception` kullanılmış, spesifik hatalar yakalanmalı |
| **Global Değişkenler** | 🟡 Orta | `_db_connection` global değişken olarak kullanılıyor |
| **Hata Mesajları Kullanıcıya** | 🟡 Orta | `print()` ile konsola yazılan hatalar kullanıcıya gösterilmiyor |
| **Dosya Yolu Doğrulama** | 🟠 Düşük | `validators.py`'deki path doğrulama yetersiz |

### 4.3 Tasarım Sorunları
| Sorun | Öncelik | Açıklama |
|-------|---------|----------|
| **Çoklu Miras Riski** | 🟡 Orta | `BaseCrudView` ve `FormDialog` benzer işler yapıyor |
| **Service Katmanı Kalınlığı** | 🟠 Düşük | Bazı service'ler sadece repository çağırıyor |
| **Controller Katmanı Gerekliliği** | 🟠 Düşük | Controller çoğu yerde service'i direct çağırıyor |
| **Veri Doğrulama Yeri** | 🟠 Düşük | Validasyon hem view'da hem service'de yapılıyor |

### 4.4 Performans Sorunları
| Sorun | Öncelik | Açıklama |
|-------|---------|----------|
| **N+1 Sorgu Problemi** | 🟡 Orta | Döngüler içinde veritabanı sorguları olabilir |
| **Lazy Loading** | 🟠 Düşük | Tüm verileri çekip bellekte filtreleme yapılıyor |
| **Bağlantı Havuzu Boyutu** | 🟠 Düşük | Max 10 bağlantı yeterli olmayabilir |

## 5. Öneriler

### 5.1 Kısa Vadeli Öneriler (Acil)
1. **Şifreleme Güncellemesi**: `hashlib.sha256` yerine `bcrypt` kullanın
2. **Environment Variables**: Tüm hassas bilgileri `.env` dosyasına taşıyın
3. **Hata Yönetimi**: Kullanıcıya anlaşılır hata mesajları gösterin
4. **Loglama**: `print()` yerine `logging` modülünü kullanın

### 5.2 Orta Vadeli Öneriler
1. **Transaction Yönetimi**: Birden fazla işlemi transaction içinde yapın
2. **Sorgu Optimizasyonu**: JOIN sorgularında N+1 sorununu çözün
3. **Test Katmanı**: Unit test ve entegrasyon test ekleyin
4. **API Dokümantasyonu**: Her fonksiyon için docstring ekleyin

### 5.3 Uzun Vadeli Öneriler
1. **Web Arayüzü**: Tkinter yerine web-based arayüz (Flask/FastAPI)
2. **REST API**: Mobil uygulama entegrasyonu için REST API
3. **Microservices**: Sınav planlama servisini ayrı bir servis olarak çıkar
4. **Redis Cache**: Sık kullanılan verileri cache'leyin

## 6. Veri Kaynakları

Bu proje mock/test verileri **kullanmaz**. Tüm veriler gerçek Excel dosyalarından gelir:

| Veri Tipi | Kaynak | Format |
|-----------|--------|--------|
| Öğrenci Listeleri | `exceller/SınıfListesi[KOD].xls` | .xls (xlrd) |
| Derslik Yakınlıkları | [`ClassroomProximityLoader._load_manual_data()`](../src/utils/classroom_proximity_loader.py:200) | Fallback (gerçek kampüs) |

**Mevcut Öğrenci Dosyaları:**
- SınıfListesi[BLM111].xls, SınıfListesi[BLM328].xls, SınıfListesi[BLM331].xls
- SınıfListesi[MAT110] (3).xls, SınıfListesi[MAT110] (4).xls
- SınıfListesi[MAT211] (1).xls, SınıfListesi[MAT213] (4).xls, SınıfListesi[MAT220] (2).xls
- SınıfListesi[SEC908].xls
- SınıfListesi[YZM119].xls, SınıfListesi[YZM326].xls, SınıfListesi[YZM329].xls, SınıfListesi[YZM332].xls

## 7. Proje Durumu (Güncel)

| Alan | Durum | Not |
|------|------|-----|
| Veritabanı & Kurulum | ✅ Tamam | Şema, trigger, öğrenci tabloları tek setup dosyasında |
| Modeller & Repositories | ✅ Tamam | CRUD + ilişki sorguları ve soft delete akışı hazır |
| Services | ✅ Tamam | Otomatik planlama, öğrenci bazlı çakışma ve derslik birleştirme çalışır durumda |
| Controllers & Views | ⚠️ Kısmi | Rol bazlı akışlar hazır; sınav ekranı dışa aktarma metotları tamamlanmadı |
| Utils | ✅ Tamam | Excel import, proximity loader, Excel generator mevcut |
| Veri Import | ✅ Tamam | Gerçek Excel dosyalarından öğrenci import mevcut |
| Güvenlik & Operasyon | ❗ Eksik | SHA256, hardcoded bilgiler, log/exception iyileştirme ihtiyacı |

**Öncelikli Açıklar**
- `ExamScheduleView` PDF/Excel dışa aktarma akışında controller metotları eksik
- Şifre hash'inin bcrypt/Argon2'ye taşınması ve `.env` temizlikleri
- Birleşik derslik kayıtlarında transaction güvenliği
- Otomatik testlerin (unit/integration) eklenmesi

## 8. Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| Veritabanı | PostgreSQL 14+ |
| ORM | Yok (Raw SQL) |
| GUI | Tkinter |
| Excel | openpyxl, xlrd |
| Veritabanı Driver | psycopg2 |
| Dil | Python 3.8+ |

## 9. Veritabanı Şeması

### Ana Tablolar
- **faculties**: Fakülteler
- **departments**: Bölümler (→ faculties)
- **classrooms**: Derslikler (→ faculties) + room_type
- **lecturers**: Öğretim üyeleri (→ departments)
- **courses**: Dersler (→ departments, → lecturers) + required_room_type
- **exam_schedule**: Sınav programı (→ courses, → classrooms)
- **users**: Kullanıcılar (→ departments)
- **students**: Öğrenciler (→ departments) ⭐
- **student_courses**: Öğrenci-ders ilişkileri (→ students, → courses) ⭐

### Trigger ve Indeksler
- `updated_at` otomatik güncelleme trigger'ı
- Yabancı anahtar ve sıklıkla aranan alanlar için indeksler
- `unique_classroom_time` unique constraint
- `student_courses(student_id, course_id)` unique constraint ⭐

## 10. Rol ve İzinler

| Rol | Açıklama | Yetkiler |
|-----|----------|----------|
| admin | Sistem yöneticisi | Tüm işlemler |
| bolum_yetkilisi | Bölüm yetkilisi | Kendi bölümü için CRUD |
| hoca | Öğretim üyesi | Sınav programı görüntüleme |
| ogrenci | Öğrenci | Sınav programı görüntüleme |

## 11. Veri İçe Aktarma (v2.0)

### 11.1 Öğrenci Bazlı Çakışma Kontrolü

Eski sistemde çakışma kontrolü sadece bölüm ve sınıf yılı bazında yapılıyordu. Yeni sistemde gerçek öğrenci listeleri üzerinden kontrol yapılır:

| Özellik | Eski Sistem | Yeni Sistem |
|---------|-------------|-------------|
| Çakışma Kontrolü | Bölüm + Yıl aynı mı? | Öğrenci kümeleri kesişimi |
| Veri Kaynağı | course.department_id + course.year | student_courses tablosu |
| Doğruluk | Tahmini (yanlış pozitif) | Kesin (gerçek veri) |

### 11.2 Excel'den Öğrenci Import

```python
from src.services.student_import_service import StudentImportService

service = StudentImportService()

# Tek dosya import
result = service.import_from_excel(
    "exceller/SınıfListesi[BLM111].xls",
    course_id=1,
    semester="2024-2025 Güz"
)

# Klasör import
results = service.import_from_excel_directory(
    "exceller/",
    semester="2024-2025 Güz"
)
```

### 11.3 Derslik Yakınlık Grafiği

```python
from src.utils.classroom_proximity_loader import get_proximity_loader

loader = get_proximity_loader()

# Komşu derslikleri al
neighbors = loader.get_neighbors("M101")

# En yakın derslikleri al
closest = loader.get_closest_classrooms(
    "M101",
    available_list,
    limit=5
)
```

## 12. İlk Kurulum

### 1. Veritabanı Kurulumu
```bash
python database/core/setup_db.py
```

### 2. Öğrenci Verisi İçe Aktarma
```python
from src.services.student_import_service import StudentImportService

service = StudentImportService()
results = service.import_from_excel_directory("exceller/", "2024-2025 Güz")
```

### 3. Admin Kullanıcı Oluşturma
Kullanıcılar manuel olarak GUI üzerinden veya SQL ile oluşturulur.
