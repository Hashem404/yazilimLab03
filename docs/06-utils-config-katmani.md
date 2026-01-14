# Utils ve Config Katmanı Dokümantasyonu

Bu belge, projedeki utility fonksiyonlarını, config ayarlarını ve uygulama başlangıç noktasını detaylandırmaktadır.

## 📁 Dosya Yapısı

```
src/
├── config/
│   ├── __init__.py
│   └── database.py          # Veritabanı konfigürasyonu
├── utils/
│   ├── __init__.py
│   ├── excel_generator.py       # Excel dosyası oluşturma (479 satır)
│   ├── student_importer.py      # Excel'den öğrenci import etme
│   ├── classroom_proximity_loader.py  # Derslik yakınlık verisi
│   └── validators.py            # Validasyon fonksiyonları (166 satır)
└── main.py                  # Uygulama başlangıç noktası (116 satır)
```

---

## 1. Config Katmanı

### 1.1 DatabaseConfig - Veritabanı Konfigürasyonu

**Dosya:** [`src/config/database.py`](../src/config/database.py) - **97 satır**

#### Amaç
PostgreSQL veritabanı bağlantı ayarlarını yönetir ve connection pool sağlar.

#### DatabaseConfig Sınıfı

```python
class DatabaseConfig:
    def __init__(self):
        self.host = os.environ.get('DB_HOST', 'localhost')
        self.port = os.environ.get('DB_PORT', '5432')
        self.database = os.environ.get('DB_NAME', 'universite_sinav_db')
        self.user = os.environ.get('DB_USER', 'postgres')
        self.password = os.environ.get('DB_PASSWORD', 'postgres')
```

#### Ortam Değişkenleri

| Değişken | Açıklama | Varsayılan |
|----------|----------|-----------|
| `DB_HOST` | Veritabanı sunucusu | `localhost` |
| `DB_PORT` | Veritabanı portu | `5432` |
| `DB_NAME` | Veritabanı adı | `universite_sinav_db` |
| `DB_USER` | Kullanıcı adı | `postgres` |
| `DB_PASSWORD` | Şifre | `postgres` |

#### Metotlar

| Metot | Açıklama | Dönüş |
|-------|----------|-------|
| `get_connection_string()` | libpq bağlantı string'i | `str` |
| `get_connection_dict()` | Bağlantı parametreleri sözlüğü | `dict` |

**Örnek Çıktı:**
```python
# get_connection_string()
"host=localhost port=5432 dbname=universite_sinav_db user=postgres password=postgres"

# get_connection_dict()
{
    'host': 'localhost',
    'port': '5432',
    'dbname': 'universite_sinav_db',
    'user': 'postgres',
    'password': 'postgres'
}
```

#### ⚠️ Güvenlik Sorunu

**Sorun:** Varsayılan şifre hardcoded olarak `postgres` olarak tanımlanmış.

```python
self.password = os.environ.get('DB_PASSWORD', 'postgres')  # Varsayılan değer güvenli değil
```

**Öneri:** Production ortamında mutlaka ortam değişkeni üzerinden şifre verilmeli.

---

### 1.2 DatabaseConnection - Connection Pool

**Dosya:** [`src/config/database.py`](../src/config/database.py)

#### Amaç
Singleton pattern ile connection pool yönetimi sağlar.

#### Yapı

```python
class DatabaseConnection:
    _instance: Optional['DatabaseConnection'] = None
    _pool: Optional[pool.SimpleConnectionPool] = None
```

#### Connection Pool Ayarları

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| `minconn` | 1 | Minimum açık bağlantı sayısı |
| `maxconn` | 10 | Maksimum açık bağlantı sayısı |

#### Metotlar

| Metot | Açıklama |
|-------|----------|
| `get_connection()` | Havuzdan bağlantı alır |
| `release_connection(conn)` | Bağlantıyı havuza geri bırakır |
| `close_all()` | Tüm bağlantıları kapatır |

#### Singleton Pattern

```python
def __new__(cls):
    if cls._instance is None:
        cls._instance = super().__new__(cls)
    return cls._instance
```

#### Global Fonksiyonlar

```python
def get_connection():
    """Global bağlantı alma fonksiyonu"""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection.get_connection()

def release_connection(conn):
    """Global bağlantı bırakma fonksiyonu"""
    global _db_connection
    if _db_connection is not None:
        _db_connection.release_connection(conn)

def close_all_connections():
    """Tüm bağlantıları kapatma fonksiyonu"""
    global _db_connection
    if _db_connection is not None:
        _db_connection.close_all()
        _db_connection = None
```

#### Kullanım Örneği

```python
from src.config.database import get_connection, release_connection

conn = get_connection()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
finally:
    release_connection(conn)
```

#### Olası Hatalar

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| `psycopg2.Error` | Bağlantı hatası | Veritabanı ayarlarını kontrol et |
| `NoneType` error | Havuz başlatılamadı | `_initialize_pool()` çağrısı kontrol et |
| `Pool exhausted` | Tüm bağlantılar kullanımda | `maxconn` artır veya bağlantıyı serbest bırak |

---

## 2. Utils Katmanı

### 2.1 ExcelGenerator - Excel Dosyası Oluşturma

**Dosya:** [`src/utils/excel_generator.py`](../src/utils/excel_generator.py) - **479 satır**

#### Amaç
Farklı veri tipleri için formatlı Excel dosyaları oluşturur. `openpyxl` kütüphanesini kullanır.

#### Özellikler

- ✅ Dict ve Object destekli veri işleme
- ✅ Otomatik tip algılama (Çakışma, İstatistik, Derslik Kullanımı, vs.)
- ✅ Formatlı başlıklar (koyu mavi arka plan, beyaz yazı)
- ✅ Otomatik sütun genişlikleri
- ✅ CSV fallback (openpyxl yoksa)

#### Ana Metot: `generate()`

```python
def generate(self, data: List[Any], output_path: str) -> bool:
    # Veri tipine göre uygun generator metodunu çağırır
```

#### Veri Tipi Algılama

| Alan | Veri Tipi | Generator Metodu |
|------|-----------|------------------|
| `type` = `classroom_conflict` veya `course1` | Çakışma | `_generate_conflict_excel()` |
| `istatistik` | İstatistik | `_generate_statistics_excel()` |
| `zaman_dilimi` | Derslik kullanımı | `_generate_classroom_usage_excel()` |
| `faculty_name` + `department_count` | Fakülte dağılımı | `_generate_faculty_excel()` |
| `course_code` | Sınav programı | `_generate_exam_dict_excel()` |
| Diğer | Generic | `_generate_generic_excel()` |

#### Yardımcı Metotlar

##### `_get_value(item, key, default)`

Dict veya object'ten değer alır:

```python
def _get_value(self, item: Any, key: str, default: Any = '') -> Any:
    if isinstance(item, dict):
        return item.get(key, default)
    else:
        return getattr(item, key, default)
```

##### `_get_column_letter(col_num)`

Sütun numarasını Excel harf formatına çevirir:

```python
# 1 -> 'A', 2 -> 'B', 27 -> 'AA', 28 -> 'AB'
```

##### `_get_exam_type_label(exam_type)`

Sınav türü etiketleri:

| Değer | Etiket |
|-------|--------|
| `midterm` | Vize |
| `final` | Final |
| `makeup` | Bütünleme |
| `quiz` | Quiz |

##### `_get_status_label(status)`

Durum etiketleri:

| Değer | Etiket |
|-------|--------|
| `planned` | Planlandı |
| `confirmed` | Onaylandı |
| `cancelled` | İptal Edildi |

#### Generator Metotları

##### `_generate_exam_dict_excel()` - Sınav Programı

**Başlıklar:**
| Tarih | Başlangıç Saati | Bitiş Saati | Ders Kodu | Ders Adı | Öğretim Üyesi | Derslik | Fakülte | Bölüm | Öğrenci Sayısı | Sınav Türü | Durum |

**Sütun Genişlikleri:** `[12, 12, 12, 12, 25, 20, 15, 15, 18, 12, 12, 12]`

##### `_generate_conflict_excel()` - Çakışma Raporu

**Başlıklar:**
| Tarih | Saat | Derslik | Ders 1 | Ders 2 | Çakışma Tipi |

**Sütun Genişlikleri:** `[12, 15, 15, 15, 15, 18]`

##### `_generate_classroom_usage_excel()` - Derslik Kullanımı

**Başlıklar:**
| Zaman Dilimi | Kullanılan Derslik | Toplam Derslik | Kullanılan Kapasite | Toplam Kapasite | Kullanım % |

**Sütun Genişlikleri:** `[15, 18, 15, 18, 15, 12]`

##### `_generate_statistics_excel()` - İstatistik Raporu

**Başlıklar:**
| İstatistik | Değer |

**İstatistik Etiketleri:**
| Anahtar | Etiket |
|--------|--------|
| `total_faculties` | Toplam Fakülte |
| `total_departments` | Toplam Bölüm |
| `total_classrooms` | Toplam Derslik |
| `total_lecturers` | Toplam Öğretim Üyesi |
| `total_courses` | Toplam Ders |
| `total_exams` | Toplam Sınav |
| `this_week_exams` | Bu Haftaki Sınavlar |
| `today_exams` | Bugünkü Sınavlar |
| `pending_exams` | Onay Bekleyen |

##### `_generate_faculty_excel()` - Fakülte Dağılımı

**Başlıklar:**
| Fakülte Adı | Fakülte Kodu | Bölüm Sayısı |

##### `_generate_generic_excel()` - Generic Dönüşüm

Herhangi bir veri tipi için otomatik dönüşüm.

##### `generate_classroom_list()` - Derslik Listesi

**Başlıklar:**
| ID | Derslik Adı | Fakülte | Kapasite | Bilgisayar |

##### `generate_course_list()` - Ders Listesi

**Başlıklar:**
| Ders Kodu | Ders Adı | Kredi | AKTS | Dönem | Öğrenci Sayısı | Öğretim Üyesi | Bölüm |

#### CSV Fallback

`openpyxl` kurulu değilse otomatik CSV olarak kaydeder:

```python
def _fallback_to_csv(self, data: List[Any], output_path: str) -> bool:
    # .xlsx -> .csv
    # UTF-8 encoding
    # Virgül ayrımlı
```

#### Olası Hatalar

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| `ImportError` | openpyxl yok | CSV fallback kullanılır |
| `AttributeError` | Yanlış veri tipi | Generic generator kullanılır |
| `FileNotFoundError` | Klasör yok | Klasör oluşturulmalı |
| `PermissionError` | Dosya kullanımda | Dosyayı kapat |

---

### 2.2 StudentImporter - Excel'den Öğrenci Import Etme

**Dosya:** [`src/utils/student_importer.py`](../src/utils/student_importer.py)

#### Amaç
Excel dosyalarından öğrenci listelerini okuyarak veritabanına import eder. Her iki Excel formatını (.xls ve .xlsx) destekler.

#### Özellikler

- ✅ `.xls` (xlrd) ve `.xlsx` (openpyxl) format desteği
- ✅ Kolon adı otomatik algılama
- ✅ Öğrenci ve öğrenci-ders ilişkisi oluşturma
- ✅ Batch insert ile performans optimizasyonu
- ✅ Hata yönetimi ve loglama

#### Sınıf Yapısı

```python
class StudentImporter:
    def __init__(self, connection):
        self.connection = connection
        self.student_repo = StudentRepository(connection)
        self.student_course_repo = StudentCourseRepository(connection)
        self.course_repo = CourseRepository(connection)
```

#### Ana Metotlar

##### `import_from_excel(file_path, course_id=None, semester=None) -> Dict`

Tek bir Excel dosyasını import eder.

**Parametreler:**
- `file_path`: Excel dosyası yolu
- `course_id`: İsteğe bağlı - Ders ID'si (student_courses için)
- `semester`: İsteğe bağlı - Dönem bilgisi

**Dönüş:** `Dict` - İşlem sonucu
```python
{
    "success": bool,
    "students_added": int,
    "student_courses_added": int,
    "errors": List[str]
}
```

**Kullanım Örneği:**
```python
from src.utils.student_importer import StudentImporter
from database.core.connection import get_connection

conn = get_connection()
importer = StudentImporter(conn)

# Tek dosya import
result = importer.import_from_excel("exceller/SınıfListesi[BLM111].xls", course_id=1)
print(f"{result['students_added']} öğrenci eklendi")
```

##### `import_from_excel_directory(directory_path, semester=None) -> Dict`

Bir klasördeki tüm Excel dosyalarını import eder.

**Parametreler:**
- `directory_path`: Klasör yolu
- `semester`: Dönem bilgisi (tüm dosyalar için)

**Dönüş:** `Dict` - Özet sonuç
```python
{
    "success": bool,
    "files_processed": int,
    "total_students_added": int,
    "total_student_courses_added": int,
    "file_results": Dict[str, Dict]  # Her dosya için ayrı sonuç
}
```

#### Kolon Algılama

İmporter,以下の kolon isimlerini otomatik olarak algılar:

| Öğrenci Numarası | Ad | Soyad | Bölüm | Sınıf | E-posta |
|-----------------|-----|-------|-------|-------|---------|
| `Öğrenci No` | `Ad` | `Soyad` | `Bölüm` | `Sınıf` | `E-posta` |
| `Ogrenci No` | `Adı` | `Soyadı` | `Bolum` | `Yil` | `Email` |
| `Numara` | `Isim` | `Soyisim` | `Department` | `Year` | `e-mail` |
| `No` | `First Name` | `Last Name` | - | - | `Mail` |
| `Öğr. No` | - | - | - | - | - |

#### Excel Formatı Desteği

**.xls formatı (xlrd):**
```python
import xlrd
workbook = xlrd.open_workbook(file_path)
sheet = workbook.sheet_by_index(0)
```

**.xlsx formatı (openpyxl):**
```python
from openpyxl import load_workbook
workbook = load_workbook(file_path)
sheet = workbook.active
```

#### Ders Kodu Algılama

Dosya adından ders kodunu çıkarır:

```python
# "SınıfListesi[BLM111].xls" -> "BLM111"
# "SınıfListesi[MAT110].xlsx" -> "MAT110"
# "students_MAT211.xls" -> "MAT211"
```

#### Örnek Excel Yapısı

```
| Öğrenci No | Ad       | Soyad    | E-posta              |
|------------|----------|----------|----------------------|
| 2021001    | Ahmet    | Yılmaz   | ahmet@example.com    |
| 2021002    | Ayşe     | Demir    | ayse@example.com     |
| 2021003    | Mehmet   | Kaya     | mehmet@example.com   |
```

#### Hata Yönetimi

| Hata Durumu | İşlem |
|-------------|-------|
| Dosya bulunamadı | `FileNotFoundError` fırlatır |
| Desteklenmeyen format | Uyarı loglar, atlar |
| Geçersiz kolon | Uyarı loglar, boş değer kullanır |
| Veritabanı hatası | `errors` listesine ekler |

#### Olası Hatalar

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| `ImportError` | xlrd veya openpyxl yok | `pip install xlrd openpyxl` |
| `FileNotFoundError` | Dosya yolu yanlış | Yolu kontrol et |
| `KeyError` | Kolon bulunamadı | Excel başlıklarını kontrol et |

---

### 2.3 ClassroomProximityLoader - Derslik Yakınlık Yükleyici

**Dosya:** [`src/utils/classroom_proximity_loader.py`](../src/utils/classroom_proximity_loader.py) - **407 satır**

#### Amaç
Derslikler arası fiziksel yakınlık bilgilerini Excel/CSV dosyasından okur ve Graph (Adjacency List) yapısında tutar. Derslik birleştirme algoritmasında kullanılır.

#### Kullanım

```python
from src.utils.classroom_proximity_loader import ClassroomProximityLoader

# Singleton instance
loader = ClassroomProximityLoader()

# Bir dersliğin komşularını al
neighbors = loader.get_neighbors("M101")  # ['S101', 'M201', 'M301', ...]

# Bir dersliğin blok bilgisini al
block = loader.get_block("M101")  # 'M'

# İki derslik yakını mı?
is_near = loader.are_neighbors("M101", "S101")  # True

# Bir dersliğe en yakın derslikleri al
closest = loader.get_closest_classrooms("M101", available_list, limit=5)
```

#### Veri Formatı

Excel/CSV formatındaki veri yapısı:

| BLOK | DERSLİK | YAKIN DERSLİK |
|------|---------|---------------|
| M | M101 | S101,M201,M301,S201,S202 |
| M | M201 | M301,M101,S201,S202 |
| S | S101 | M101,S201,S202,M201,M301 |

#### ClassroomNode Sınıfı

```python
@dataclass
class ClassroomNode:
    """Derslik düğümü"""
    name: str
    block: str
    neighbors: Set[str]
    
    def add_neighbor(self, neighbor_name: str) -> None:
        """Komşu derslik ekle"""
    
    def is_neighbor(self, other_name: str) -> bool:
        """Diğer derslik komşu mu?"""
```

#### Ana Metotlar

##### `get_neighbors(classroom_name)` - Komşuları Getir

```python
def get_neighbors(self, classroom_name: str) -> List[str]:
    """
    Bir dersliğin komşularını döndürür.
    
    Args:
        classroom_name: Derslik adı (örn: "M101")
        
    Returns:
        Komşu derslik listesi. Derslik bulunamazsa boş liste.
    """
```

##### `are_neighbors(classroom1, classroom2)` - Komşuluk Kontrolü

```python
def are_neighbors(self, classroom1: str, classroom2: str) -> bool:
    """
    İki dersliğin birbirine yakın olup olmadığını kontrol eder.
    """
```

##### `get_available_neighbors_for_combination()` - Birleştirme İçin Komşular

```python
def get_available_neighbors_for_combination(
    self,
    classroom_name: str,
    available_classrooms: List[str]
) -> List[str]:
    """
    Bir dersliğin, kullanılabilir derslikler arasındaki komşularını döndürür.
    
    Bu metod, derslik birleştirme algoritmasında kullanılır.
    Ana dersliğin komşuları arasından, kullanılabilir olanları filtreler.
    """
```

##### `get_closest_classrooms()` - En Yakın Derslikler

```python
def get_closest_classrooms(
    self,
    classroom_name: str,
    available_classrooms: List[str],
    limit: int = 5
) -> List[str]:
    """
    Bir dersliğe en yakın derslikleri döndürür.
    
    Komşuları önceliklendirir, ardından aynı bloktaki derslikleri değerlendirir.
    """
```

#### Fallback Manuel Veri

Dosya bulunamazsa varsayılan veri kullanılır:

```python
manual_data = [
    ("M", "M101", "S101,M201,M301,S201,S202"),
    ("M", "M201", "M301,M101,S201,S202"),
    ("M", "M301", "M201,M101,S201,S202"),
    ("S", "S101", "M101,S201,S202,M201,M301"),
    # ... daha fazla derslik
]
```

#### Dosya Yolları

```python
DEFAULT_FILE_PATH = "exceller/Derslik Yakınlık (1).xlsx"
DEFAULT_CSV_PATH = "exceller/Derslik Yakınlık (1).csv"
```

#### Singleton Pattern

```python
def get_proximity_loader() -> ClassroomProximityLoader:
    """
    Singleton olarak proximity loader instance'ı döndürür.
    Böylece tüm uygulama boyunca tek bir instance kullanılır.
    """
```

#### Graph İstatistikleri

```python
def get_graph_stats(self) -> Dict:
    """Graph istatistiklerini döndürür"""
    return {
        'total_classrooms': len(self._classroom_graph),
        'total_blocks': len(self._block_classrooms),
        'blocks': {block: len(classrooms) for block, classrooms in self._block_classrooms.items()},
        'classrooms': list(self._classroom_graph.keys())
    }
```

---

### 2.4 Validators - Validasyon Fonksiyonları

**Dosya:** [`src/utils/validators.py`](../src/utils/validators.py) - **166 satır**

#### Amaç
Genel amaçlı validasyon fonksiyonları sağlar.

#### Validasyon Fonksiyonları

##### `validate_file_path(path, extension)` - Dosya Yolu Validasyonu

```python
def validate_file_path(path: str, extension: str) -> bool:
    # 1. Uzantı kontrolü
    # 2. Path traversal kontrolü (..)
    # 3. Geçersiz karakter kontrolü
    # 4. Absolute path kontrolü
```

**Kontrol Edilen Durumlar:**
- Dosya uzantısı doğru mu?
- Path traversal içeriyor mu? (`..`)
- Geçersiz karakter var mı? (`<>:"|?*` ve kontrol karakterleri)

**Örnek:**
```python
validate_file_path("rapor.xlsx", "xlsx")  # True
validate_file_path("../etc/passwd.xlsx", "xlsx")  # False (path traversal)
validate_file_path("rapor<test>.xlsx", "xlsx")  # False (geçersiz karakter)
```

##### `validate_email(email)` - E-posta Validasyonu

```python
pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
```

**Geçerli Örnekler:**
- `test@example.com`
- `user.name+tag@domain.co.uk`
- `user123@sub.domain.com`

**Geçersiz Örnekler:**
- `test@` (eksik domain)
- `@example.com` (eksik local)
- `test..email@example.com` (çift nokta)

##### `validate_phone(phone)` - Telefon Numarası Validasyonu

```python
# Boş string -> True (opsiyonel alan)
# 10-15 basamak, + opsiyonel
# Boşluk, tire, parantez ignore edilir
```

**Geçerli Örnekler:**
- `+905551234567`
- `0555 123 45 67`
- `(0555) 123-45-67`

##### `validate_date_format(date_str, format)` - Tarih Format Validasyonu

```python
def validate_date_format(date_str: str, format: str = '%Y-%m-%d') -> bool:
    # Varsayılan: YYYY-MM-DD
```

**Geçerli Örnekler:**
- `2025-01-15` (varsayılan format)
- `15/01/2025` (`%d/%m/%Y` formatı)

##### `validate_password_strength(password)` - Şifre Güçlüğü

**Kriterler:**
- En az 8 karakter
- En az bir büyük harf
- En az bir küçük harf
- En az bir rakam
- En az bir özel karakter

**Dönüş:** `(bool, message)` - `(geçerli_mi, hata_mesajı)`

**Örnek:**
```python
validate_password_strength("Pass123!")
# (True, None)

validate_password_strength("weak")
# (False, "Şifre en az 8 karakter olmalıdır")
```

##### `sanitize_filename(filename)` - Dosya Adı Temizleme

```python
# Geçersiz karakterler -> _
# Çift alt tire -> tek tire
# Başlangıç/sondaki tireleri temizle
```

**Örnek:**
```python
sanitize_filename("file<>name.xlsx")
# "file_name.xlsx"

sanitize_filename("test___file")
# "test_file"
```

##### `validate_required_fields(data, required_fields)` - Zorunlu Alanlar

```python
# Dönüş: (bool, list) - (tümü_dolu_mu, eksik_alanlar)
```

**Örnek:**
```python
validate_required_fields({'name': 'Ahmet', 'email': ''}, ['name', 'email'])
# (False, ['email'])
```

##### `validate_range(value, min_val, max_val)` - Aralık Validasyonu

```python
# Sayısal aralık kontrolü
# String -> float dönüşümü dener
```

##### `validate_turkish_identity_number(tckn)` - TCKN Validasyonu

**Kurallar:**
- 11 basamak
- Sadece rakam
- İlk basamak 0 olamaz
- 10. basamak = (İlk 9 basamağın toplamı) % 10
- 11. basamak = (İlk 10 basamağın toplamı) % 10

**Örnek:**
```python
validate_turkish_identity_number("10000000146")  # Geçerli örnek
```

##### `is_positive_integer(value)` - Pozitif Tam Sayı

```python
# Int dönüşümü ve > 0 kontrolü
```

##### `is_valid_url(url)` - URL Validasyonu

**Desteklenen Formatlar:**
- `http://` veya `https://`
- Domain veya IP adresi
- `localhost`
- Opsiyonel port

**Geçerli Örnekler:**
- `https://example.com`
- `http://localhost:8000`
- `https://192.168.1.1:3000`

---

## 3. Main - Uygulama Başlangıç Noktası

**Dosya:** [`src/main.py`](../src/main.py) - **116 satır**

### Application Sınıfı

#### Amaç
Tkinter uygulamasının ana sınıfı. View yönetimi ve stil konfigürasyonunu içerir.

#### Yapı

```python
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title('Üniversite Sınav Programı Sistemi')
        self.geometry('1400x800')
        self.minsize(1200, 700)
        
        self._center_window()
        self._setup_styles()
        
        self.auth_controller = AuthController()
        self.container = tk.Frame(self)
        self.container.pack(fill='both', expand=True)
        
        self.show_login()
```

#### Pencere Ayarları

| Ayar | Değer | Açıklama |
|------|-------|----------|
| `title` | Üniversite Sınav Programı Sistemi | Pencere başlığı |
| `geometry` | 1400x800 | Pencere boyutu |
| `minsize` | 1200x700 | Minimum boyut |

#### View Yönetimi

| Metot | Açıklama |
|-------|----------|
| `show_login()` | Giriş ekranını gösterir |
| `show_dashboard()` | Ana paneli gösterir |
| `_clear_container()` | Mevcut view'ı temizler |
| `on_login_success()` | Başarılı giriş callback'i |

#### Stil Konfigürasyonu

##### ttk.Style Ayarları

**Tema:** `clam`

```python
style.theme_use('clam')
```

##### Buton Stilleri

```python
# Primary.TButton - Mavi butonlar
style.configure('Primary.TButton',
               background='#3498db',
               foreground='white',
               padding=(20, 10),
               font=('Segoe UI', 10))

# Success.TButton - Yeşil butonlar
style.configure('Success.TButton',
               background='#27ae60',
               foreground='white',
               padding=(15, 8),
               font=('Segoe UI', 10))

# Danger.TButton - Kırmızı butonlar
style.configure('Danger.TButton',
               background='#e74c3c',
               foreground='white',
               padding=(15, 8),
               font=('Segoe UI', 10))
```

##### Treeview Stilleri

```python
# Tablo satırları
style.configure('Treeview',
               background='white',
               foreground='#2c3e50',
               rowheight=30,
               fieldbackground='white',
               font=('Segoe UI', 10))

# Tablo başlıkları
style.configure('Treeview.Heading',
               background='#3498db',
               foreground='white',
               font=('Segoe UI', 10, 'bold'))

# Seçili satır
style.map('Treeview',
          background=[('selected', '#3498db')],
          foreground=[('selected', 'white')])
```

#### Uygulama Akışı

```
main()
   ↓
Application.__init__()
   ↓
_setup_styles()
   ↓
show_login()
   ↓
[LoginView]
   ↓
on_login_success()
   ↓
show_dashboard()
   ↓
[DashboardView]
```

#### main() Fonksiyonu

```python
def main():
    try:
        app = Application()
        app.run()
    except Exception as e:
        messagebox.showerror('Hata', f'Uygulama başlatılamadı:\n{str(e)}')
        raise
```

#### Hata Yönetimi

Uygulama başlatma hatası durumunda messagebox ile gösterilir.

---

## 4. Kullanım Örnekleri

### 4.1 Veritabanı Bağlantısı

```python
from src.config.database import get_connection, release_connection

conn = get_connection()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL version: {version}")
finally:
    release_connection(conn)
```

### 4.2 Excel Oluşturma

```python
from src.utils.excel_generator import ExcelGenerator
from datetime import date

generator = ExcelGenerator()

# Sınav programı
data = [
    {
        'exam_date': date(2025, 1, 15),
        'start_time': '09:00',
        'end_time': '11:00',
        'course_code': 'CS101',
        'course_name': 'Programlamaya Giriş',
        'lecturer_name': 'Dr. Ahmet Yılmaz',
        'classroom_name': 'A-101',
        'faculty_name': 'Mühendislik Fakültesi',
        'student_count': 120,
        'exam_type': 'final',
        'status': 'planned'
    }
]

success = generator.generate(data, 'sinav_programi.xlsx')
```

### 4.3 Validasyon Kullanımı

```python
from src.utils.validators import (
    validate_email,
    validate_password_strength,
    validate_required_fields
)

# E-posta kontrolü
if not validate_email("test@example.com"):
    print("Geçersiz e-posta")

# Şifre kontrolü
valid, msg = validate_password_strength("Pass123!")
if not valid:
    print(msg)

# Zorunlu alan kontrolü
data = {'name': 'Ahmet', 'email': ''}
valid, missing = validate_required_fields(data, ['name', 'email'])
if not valid:
    print(f"Eksik alanlar: {missing}")
```

---

## 5. Olası Hatalar ve Çözümler

### 5.1 Config Hataları

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| `psycopg2.OperationalError` | Veritabanı bağlanamıyor | Host/port/user/pass kontrol et |
| `FATAL: database ... does not exist` | Veritabanı yok | `setup_db.py` çalıştır |
| `FATAL: password authentication failed` | Şifre yanlış | `.env` dosyasını kontrol et |
| `Pool exhausted` | Bağlantı havuzu doldu | `release_connection()` çağrısı kontrol et |

### 5.2 Excel Hataları

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| `ImportError` | openpyxl yok | CSV fallback kullanılır |
| `PermissionError` | Dosya açık | Dosyayı kapat |
| `ValueError` | Yanlış veri tipi | Generic generator kullanılır |
| `FileNotFoundError` | Klasör yok | Klasör oluştur |

### 5.3 Validator Hataları

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| `TypeError` | Yanlış tip | String dönüşümü yap |
| `AttributeError` | Dict yerine object | `getattr()` kontrol et |
| `ValueError` | Tarih formatı | Format string'i kontrol et |

### 5.4 Main Hataları

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| `TclError` | Tkinter başlatılamadı | DISPLAY değişkenini kontrol et (Linux) |
| `ImportError` | Modül bulunamadı | `sys.path` kontrol et |
| `AttributeError` | View import hatası | Modül yolu kontrol et |

---

## 6. Öneriler

### 6.1 Config İyileştirmeleri

1. **Environment Config:** `.env` dosyası kullanımı (python-dotenv)
2. **Config Validation:** Ayarları başlangıçta validate et
3. **Connection Retry:** Bağlantı hatasında yeniden deneme
4. **Connection Timeout:** Bağlantı zaman aşımı ayarı
5. **SSL Mode:** SSL/TLS bağlantı desteği

### 6.2 Utils İyileştirmeleri

1. **Logging:** Print yerine logging kullanımı
2. **Excel Templates:** Şablon dosya desteği
3. **Async Excel:** Büyük dosyalar için async işleme
4. **Validation Rules:** YAML/JSON ile tanımlanabilir kurallar
5. **Error Messages:** Türkçe/İngilizce dil desteği

### 6.3 Main İyileştirmeleri

1. **Config File:** Konfigürasyon dosyası desteği
2. **Argument Parsing:** Komut satırı argümanları
3. **Logging:** Loglama sistemi
4. **Crash Reporting:** Hata raporlama
5. **Auto Update:** Otomatik güncelleme kontrolü

### 6.4 Genel Öneriler

1. **Type Hints:** Tüm fonksiyonlara type hint ekle
2. **Docstrings:** Google/NumPy style docstring kullan
3. **Unit Tests:** Her modül için test yaz
4. **Profiling:** Performans analizi yap
5. **Documentation:** API dokümantasyonu oluştur (Swagger/OpenAPI)
