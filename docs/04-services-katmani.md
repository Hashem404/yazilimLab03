# Services Katmanı Dokümantasyonu

Bu belge, projedeki tüm service sınıflarının iş mantıklarını, validasyonlarını ve olası hatalarını detaylandırmaktadır.

## 📁 Servis Dosyaları

```
src/services/
├── __init__.py
├── auth_service.py          # Kimlik doğrulama servisi
├── faculty_service.py       # Fakülte servisi
├── department_service.py    # Bölüm servisi
├── lecturer_service.py      # Öğretim görevlisi servisi
├── course_service.py        # Ders servisi
├── classroom_service.py     # Derslik servisi
├── exam_schedule_service.py # Sınav programı servisi
├── scheduler_service.py     # Otomatik planlama servisi
└── student_import_service.py # Öğrenci içe aktarma servisi ⭐ YENİ
```

---

## 1. AuthService - Kimlik Doğrulama Servisi

**Dosya:** [`src/services/auth_service.py`](../src/services/auth_service.py)

### Amaç
Kullanıcı girişi, çıkışı, yetki kontrolü ve şifre yönetimi işlemlerini yönetir.

### Özellikler

| Özellik | Açıklama |
|---------|----------|
| Oturum Yönetimi | `_current_user` ile oturum durumu takibi |
| Şifre Doğrulama | SHA256 hash ile şifre kontrolü |
| Yetki Kontrolü | Rol tabanlı izin sistemi |

### Metotlar

#### `login(username, password)` - Kullanıcı Girişi
```python
def login(self, username: str, password: str) -> Tuple[bool, str]
```

**Validasyonlar:**
- Kullanıcı adı ve şifre boş olamaz
- Kullanıcı bulunmalıdır
- Kullanıcı aktif olmalıdır (`is_active = True`)
- Şifre doğru olmalıdır

**Olası Hatalar:**
- `"Kullanıcı adı ve şifre gereklidir."`
- `"Kullanıcı bulunamadı."`
- `"Bu hesap devre dışı bırakılmıştır."`
- `"Şifre hatalı."`

**Güvenlik Sorunu:** ⚠️
```python
# Kritik güvenlik açığı: SHA256 kullanılıyor
if not user.check_password(password):  # User modelinde SHA256
```

#### `change_password(old_password, new_password)` - Şifre Değiştirme
```python
def change_password(self, old_password: str, new_password: str) -> Tuple[bool, str]
```

**Validasyonlar:**
- Kullanıcı giriş yapmış olmalı
- Eski şifre doğru olmalı
- Yeni şifre en az 6 karakter olmalı

**Olası Hatalar:**
- `"Oturum açmanız gerekiyor."`
- `"Mevcut şifre hatalı."`
- `"Yeni şifre en az 6 karakter olmalıdır."`

#### `register_user(...)` - Kullanıcı Kaydı
```python
def register_user(self, username, password, email, first_name, last_name, role)
```

**Yetki Gereksinimi:** `manage_users` izni

**Validasyonlar:**
- Kullanıcı adı benzersiz olmalı
- E-posta benzersiz olmalı
- Şifre en az 6 karakter

### Rol Kontrolü Metotları

| Metot | Açıklama |
|-------|----------|
| `is_admin()` | Admin rolü kontrolü |
| `is_bolum_yetkilisi()` | Bölüm yetkilisi kontrolü |
| `is_hoca()` | Öğretim görevlisi kontrolü |
| `is_ogrenci()` | Öğrenci rolü kontrolü |
| `has_permission(permission)` | İzin kontrolü |

### Kullanıcı Bazlı Bilgi Getirme ⭐ YENİ

#### `get_user_info()` - Kullanıcı Bilgileri (Kişiselleştirilmiş)

```python
def get_user_info(self) -> Optional[dict]:
```

**Dönüş Değeri:**
Kullanıcı rolüne göre ek bilgiler içerir:

```python
# Genel bilgiler (tüm roller)
{
    'id': int,
    'username': str,
    'full_name': str,
    'email': str,
    'role': str,
    'department_id': int
}

# Öğrenci için ek bilgiler
{
    ...
    'student_id': int,      # Öğrenci tablosundaki ID
    'student_number': str   # Öğrenci numarası
}

# Hoca için ek bilgiler
{
    ...
    'lecturer_id': int      # Lecturer tablosundaki ID
}
```

**Eşleştirme Mantığı:**
- Öğrenci: Email veya username ile `students` tablosundan aranır
- Hoca: Email veya ad/soyad eşleşmesi ile `lecturers` tablosundan aranır

---

## 2. FacultyService - Fakülte Servisi

**Dosya:** [`src/services/faculty_service.py`](../src/services/faculty_service.py)

### İş Mantığı

#### `create(name, code, dean_name)` - Fakülte Oluşturma

**Validasyonlar:**
```python
# 1. Ad ve kod zorunlu
if not name or not name.strip():
    return False, "Fakülte adı gereklidir.", None

# 2. Kod benzersiz olmalı
existing = self.repository.get_by_code(code.strip().upper())
if existing:
    return False, "Bu fakülte kodu zaten kullanılıyor.", None

# 3. Kod otomatik büyük harfe çevrilir
code = code.strip().upper()
```

**Olası Hatalar:**
- `"Fakülte adı gereklidir."`
- `"Fakülte kodu gereklidir."`
- `"Bu fakülte kodu zaten kullanılıyor."`

#### `update(faculty_id, name, code, dean_name)` - Fakülte Güncelleme

**Validasyonlar:**
- Fakülte bulunmalı
- Ad ve kod zorunlu
- Kod sadece kendi haricinde benzersiz olmalı

#### `delete(faculty_id)` - Fakülte Silme

**Soft Delete:** `is_active = False` olarak işaretlenir.

⚠️ **Potansiyel Sorun:** Fakülte silindiğinde bağlı bölümler, dersler ve sınavlar ne olur? (Cascade delete kontrolü yok)

---

## 3. DepartmentService - Bölüm Servisi

**Dosya:** [`src/services/department_service.py`](../src/services/department_service.py)

### İş Mantığı

#### `create(faculty_id, name, code, head_name)` - Bölüm Oluşturma

**Validasyonlar:**
```python
# 1. Fakülte seçimi zorunlu
if not faculty_id:
    return False, "Fakülte seçimi gereklidir.", None

# 2. Ad ve kod zorunlu
if not name or not code:
    return False, "Bölüm adı/kodu gereklidir.", None

# 3. Kod benzersiz olmalı
existing = self.repository.get_by_code(code.strip().upper())
```

**Olası Hatalar:**
- `"Fakülte seçimi gereklidir."`
- `"Bölüm adı gereklidir."`
- `"Bölüm kodu gereklidir."`
- `"Bu bölüm kodu zaten kullanılıyor."`

#### `get_by_faculty_id(faculty_id)` - Fakülteye Göre Bölümler

Fakülte ID'sine göre tüm bölümleri getirir.

---

## 4. LecturerService - Öğretim Görevlisi Servisi

**Dosya:** [`src/services/lecturer_service.py`](../src/services/lecturer_service.py)

### Yardımcı Fonksiyonlar

#### `normalize_turkish_chars(text)` - Türkçe Karakter Normalizasyonu
```python
def normalize_turkish_chars(text: str) -> str:
    replacements = {
        'ı': 'i', 'İ': 'i', 'ğ': 'g', 'Ğ': 'g',
        'ü': 'u', 'Ü': 'u', 'ş': 's', 'Ş': 's',
        'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c'
    }
```

#### `generate_email(first_name, last_name)` - E-posta Oluşturma
```python
# "Ahmet Yılmaz" -> "ahmet.yilmaz@kstu.edu.tr"
# "Mehmet Demir" -> "mehmet.demir@kstu.edu.tr"
# E-posta varsa: "mehmet.demir1@kstu.edu.tr", "mehmet.demir2@kstu.edu.tr"
```

### İş Mantığı

#### `create(...)` - Öğretim Görevlisi Oluşturma

**Validasyonlar:**
```python
# 1. Bölüm seçimi zorunlu
# 2. Ad, soyad ve unvan zorunlu
# 3. E-posta otomatik oluşturulur (verilmezse)
# 4. E-posta benzersiz olmalı
# 5. Müsait günler varsayılan olarak tüm hafta içi
```

**E-posta Çakışma Çözümü:**
```python
# Eğer e-posta zaten kullanılıyorsa:
# "ahmet.yilmaz@kstu.edu.tr" -> "ahmet.yilmaz1@kstu.edu.tr"
counter = 1
while existing:
    email = base_email.replace('@', f'{counter}@')
    counter += 1
```

**Olası Hatalar:**
- `"Bölüm seçimi gereklidir."`
- `"Ad gereklidir."`
- `"Soyad gereklidir."`
- `"Unvan gereklidir."`

#### `update_available_days(lecturer_id, available_days)` - Müsait Günler Güncelleme

```python
# Sadece geçerli günler kabul edilir
valid_days = [d for d in available_days if d in ALL_WEEKDAYS]
```

### Unvan Listesi

```python
def get_titles(self) -> List[str]:
    return [
        "Prof. Dr.",
        "Doç. Dr.",
        "Dr. Öğr. Üyesi",
        "Öğr. Gör. Dr.",
        "Öğr. Gör.",
        "Arş. Gör. Dr.",
        "Arş. Gör."
    ]
```

---

## 5. CourseService - Ders Servisi

**Dosya:** [`src/services/course_service.py`](../src/services/course_service.py)

### İş Mantığı

#### `create(...)` - Ders Oluşturma

**Parametreler:**
- `department_id`: Zorunlu
- `lecturer_id`: Opsiyonel
- `code`, `name`: Zorunlu
- `credit`: Sıfır veya pozitif
- `year`: 1-4 arası
- `semester`: 1-2 arası
- `period`: 1-8 arası (year ve semester hesaplanır)
- `exam_type`: "Yazılı", "Sözlü", "Uygulama"
- `exam_duration`: 30, 60, 90, 120, 240, 360, 480 dakika (YENİ: 4-8 saat desteği)
- `course_type`: "Zorunlu", "Seçmeli", "Proje"
- `required_room_type`: "STANDART", "LAB", "OFIS", "DEKANLIK", "BILGISALONU", "KONFERANS", "ANY" (YENİ)

**Period Hesaplama:**
```python
if period is not None:
    year = ((period - 1) // 2) + 1  # 1-2 -> 1, 3-4 -> 2, 5-6 -> 3, 7-8 -> 4
    semester = ((period - 1) % 2) + 1  # Tek -> 1, Çift -> 2
```

**Proje Dersi Kontrolü:**
```python
if course_type == 'Proje':
    has_exam = False  # Proje derslerinin sınavı yok
```

**Sınav Süresi Validasyonu (YENİ):**
```python
# Geçerli sınav süreleri (30, 60, 90, 120, 240, 360, 480 dakika)
valid_durations = [d[0] for d in EXAM_DURATION_OPTIONS]
if has_exam and exam_duration not in valid_durations:
    exam_duration = 60
```

**Oda Tipi Validasyonu (YENİ):**
```python
# Normalize required_room_type
normalized_room_type = required_room_type.upper()
if normalized_room_type not in REQUIRED_ROOM_TYPE_MAP:
    normalized_room_type = "ANY"
```

**Olası Hatalar:**
- `"Bölüm seçimi gereklidir."`
- `"Ders kodu gereklidir."`
- `"Ders adı gereklidir."`
- `"Kredi sıfır veya pozitif olmalıdır."`
- `"Bu ders kodu zaten kullanılıyor."`

#### `update(...)` - Ders Güncelleme

Aynı validasyonlar, güncelleme için de geçerli.

#### Yeni Metotlar (YENİ)

| Metot | Açıklama |
|-------|----------|
| `get_exam_duration_options()` | Sınav süresi seçeneklerini döndürür |
| `get_required_room_type_options()` | Gereken oda tipi seçeneklerini döndürür |

---

## 6. ClassroomService - Derslik Servisi

**Dosya:** [`src/services/classroom_service.py`](../src/services/classroom_service.py)

### İş Mantığı

#### `create(name, faculty_id, capacity, has_computer, is_suitable, room_type)` - Derslik Oluşturma

**Parametreler:**
- `name`: Derslik adı (Zorunlu)
- `faculty_id`: Fakülte ID (Zorunlu)
- `capacity`: Kapasite (Pozitif olmalı)
- `has_computer`: Bilgisayarlı mı?
- `is_suitable`: Sınav için uygun mu?
- `room_type`: Oda tipi (YENİ - Varsayılan: "STANDART")

**Validasyonlar:**
```python
# 1. Ad zorunlu
# 2. Fakülte seçimi zorunlu
# 3. Kapasite > 0 olmalı
if capacity <= 0:
    return False, "Kapasite sıfırdan büyük olmalıdır.", None

# 4. Oda tipi normalize et
normalized_type = room_type.upper()
if normalized_type not in CLASSROOM_TYPE_MAP:
    normalized_type = "STANDART"
```

#### `get_available_for_exam(exam_date, start_time, end_time, min_capacity, room_type)` - YENİ

Belirtilen tarih ve saatte müsait olan derslikleri bulur. İsteğe bağlı oda tipi filtresi eklenmiştir.

**Parametreler:**
- `exam_date`: Sınav tarihi
- `start_time`: Başlangıç saati
- `end_time`: Bitiş saati
- `min_capacity`: Minimum kapasite (Varsayılan: 0)
- `room_type`: Oda tipi filtresi (YENİ - Opsiyonel)

**Mantık:**
1. Belirtilen zaman diliminde müsait derslikleri getir
2. Oda tipi filtresi uygula (eğer belirtilmişse)
3. Minimum kapasite filtresi uygula

```python
available = self.repository.get_available_for_exam(exam_date, start_time, end_time, room_type)
if min_capacity > 0:
    available = [c for c in available if c.capacity >= min_capacity]
return available
```

#### Yeni Metotlar (YENİ)

| Metot | Açıklama |
|-------|----------|
| `get_by_room_type(room_type)` | Belirli bir tipteki derslikleri getirir |
| `get_by_types(room_types)` | Birden fazla tipteki derslikleri getirir |
| `get_room_types()` | Mevcut derslik tiplerini döndürür |
| `get_exam_suitable(room_type)` | Sınav için uygun derslikleri getirir (oda tipi filtreli) |
| `get_suitable_with_capacity(min_capacity, room_type)` | Kapasite ve oda tipine göre uygun derslikleri getirir |

---

## 7. ExamScheduleService - Sınav Programı Servisi

**Dosya:** [`src/services/exam_schedule_service.py`](../src/services/exam_schedule_service.py)

### Sabitler

```python
WEEKDAY_NAMES = {
    0: 'Pazartesi', 1: 'Salı', 2: 'Çarşamba',
    3: 'Perşembe', 4: 'Cuma', 5: 'Cumartesi', 6: 'Pazar'
}

DAY_ALIASES = {
    'pazartesi': 'Pazartesi', 'sali': 'Salı', 'salı': 'Salı',
    'carsamba': 'Çarşamba', 'çarsamba': 'Çarşamba', 'çarşamba': 'Çarşamba',
    'persembe': 'Perşembe', 'perşembe': 'Perşembe', 'cuma': 'Cuma'
}
```

### Öğrenci Bazlı Çakışma Kontrolü ⭐ (Yeni Özellik)

#### `use_student_based_conflict` Parametresi

`ExamScheduleService` ve `SchedulerService` sınıfları artık **öğrenci bazlı çakışma kontrolü** destekler:

```python
# Öğrenci bazlı kontrol (Yeni - varsayılan)
service = ExamScheduleService(use_student_based_conflict=True)

# Bölüm/yıl bazlı kontrol (Eski sistem)
service = ExamScheduleService(use_student_based_conflict=False)
```

**Algoritma Karşılaştırma:**

| Yöntem | Çakışma Kontrolü | Açıklama | Doğruluk |
|--------|-----------------|----------|----------|
| `use_student_based_conflict=True` | Öğrenci kümeleri kesişimi | Gerçek öğrenci listeleri üzerinden kontrol | Kesin |
| `use_student_based_conflict=False` | Bölüm + Yıl aynı mı? | Eski sistem: bölüm ve sınıf yılı aynıysa çakışma var | Tahmini |

**Öğrenci Bazlı Algoritma:**

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

#### Veritabanı Sorguları

```python
# Tek ders için öğrenci numaraları
def get_student_numbers_by_course(course_id: int) -> Set[str]:
    query = """
        SELECT s.student_number
        FROM student_courses sc
        INNER JOIN students s ON sc.student_id = s.id
        WHERE sc.course_id = %s AND sc.is_active = TRUE AND s.is_active = TRUE
    """

# Çoklu ders için (performanslı)
def get_student_numbers_by_courses(course_ids: List[int]) -> Dict[int, Set[str]]:
    query = """
        SELECT sc.course_id, s.student_number
        FROM student_courses sc
        INNER JOIN students s ON sc.student_id = s.id
        WHERE sc.course_id = ANY(%s) AND sc.is_active = TRUE AND s.is_active = TRUE
    """
```

#### Öğrenci Verisi Hazırlama

Öğrenci bazlı çakışma kontrolü için önce öğrenci verileri veritabanına eklenmelidir:

```python
from src.utils.student_importer import StudentImporter

# Excel'den öğrenci import et
importer = StudentImporter()
result = importer.import_from_excel(
    "exceller/SınıfListesi[BLM111].xls",
    course_id=1,
    semester="2024-2025 Güz"
)
```

### Validasyon Metotları

#### `validate_exam_constraints()` - Sınav Kısıtlama Kontrolü

**Kontroller:**

1. **Ders Varlığı:** Ders bulunmalı
2. **Derslik Varlığı:** Derslik bulunmalı
3. **Ders Tekrarı:** Aynı ders için aynı tip sınav zaten planlanmış mı?
4. **Derslik Çakışması:** Derslik belirtilen saatte müsait mi?
5. **Öğrenci Çakışması:**
   - Yeni sistem: Gerçek öğrenci kümeleri kesişimi
   - Eski sistem: Aynı bölüm/yıldaki öğrenciler için çakışma
6. **Kapasite:** Derslik kapasitesi yeterli mi?
7. **Hoca Müsaitliği:** Hoca bu gün müsait mi?
8. **Hoca Çakışması:** Hoca başka bir sınava girecek mi?
9. **Sınav Süresi:** Planlanan süre yeterli mi?

**Örnek Hata Mesajları:**
```python
# Ders tekrarı
"Bu ders için zaten bir Final sınavı planlanmış. Bir ders için birden fazla sınav saati atanamaz."

# Derslik çakışması
"Bu derslik (A-101) belirtilen tarih ve saatte başka bir sınav için ayrılmış."

# Öğrenci çakışması (Öğrenci bazlı)
"2 ortak öğrenci var. 'BLM101 - Programlama' dersi ile çakışıyor."

# Öğrenci çakışması (Eski sistem)
"Aynı bölüm ve yıldaki öğrenciler için saat çakışması var. 'CS101 - Programlama' dersi ile çakışıyor."

# Kapasite
"Öğrenci sayısı (150) derslik kapasitesini (100) aşıyor."

# Hoca müsait değil
"Öğretim üyesi (Ahmet Yılmaz) bu gün (Pazartesi) müsait değil."

# Hoca çakışması
"Öğretim üyesinin (Ahmet Yılmaz) bu saatte başka bir sınavı var: 'CS102 - Veri Yapıları'"

# Süre uyuşmazlığı
"Planlanan süre (90 dk) dersin sınav süresinden (120 dk) kısa."
```

#### `validate_multi_classroom_exam()` - Çoklu Derslik Validasyonu

Birden fazla dersliğin birleştirilerek kullanıldığı sınavlar için validasyon.

**Ek Kontroller:**
- En az bir derslik seçilmeli
- Toplam kapasite öğrenci sayısından fazla olmalı
- Tüm derslikler müsait olmalı
- Tüm derslikler sınav için uygun olmalı (`is_suitable = True`)

### CRUD Operasyonları

#### `create()` - Tek Derslik Sınav Oluşturma

```python
def create(self, course_id, classroom_id, exam_date, start_time, end_time, 
           exam_type="final", notes=None)
```

#### `create_multi_classroom()` - Çoklu Derslik Sınav Oluşturma

```python
def create_multi_classroom(self, course_id, classroom_ids, exam_date, 
                           start_time, end_time, exam_type="final", notes=None)
```

**Birleşik Derslik Mantığı:**
```python
# Ana derslik (ilk seçilen)
primary_classroom_id = classroom_ids[0]

# Ek derslikler için not
for i, additional_classroom in enumerate(classroom_ids[1:], start=2):
    notes = f"Birleşik sınav ({i}/{len(classroom_ids)}) - Ana derslik: {primary_name}"
```

### Sınav Türleri

| Değer | Label |
|-------|-------|
| `midterm` | Vize |
| `final` | Final |
| `makeup` | Bütünleme |
| `quiz` | Quiz |

---

## 8. SchedulerService - Otomatik Planlama Servisi ⭐

**Dosya:** [`src/services/scheduler_service.py`](../src/services/scheduler_service.py) - **1245 satır**

### Amaç
Greedy + Backtracking yaklaşımı ile otomatik sınav programı oluşturur.

### Veri Yapıları

#### `TimeSlot` - Zaman Dilimi
```python
@dataclass
class TimeSlot:
    start_time: time
    end_time: time
    base_slot: bool = True  # Bu slot temel slot mu (birleştirilebilir)?
    
    def overlaps(self, other: 'TimeSlot') -> bool:
        # İki zaman dilimi çakışıyor mu?
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)
    
    def duration_minutes(self) -> int:
        # Dakika cinsinden süre
    
    def fits_duration(self, duration_minutes: int) -> bool:
        # Belirli bir süreye uyum sağlıyor mu?
    
    def can_combine_with(self, other: 'TimeSlot', break_minutes: int = 30) -> bool:
        # İki slot birleştirilebilir mi? (30 dk ara fark tolere edilir)
    
    @staticmethod
    def combine_slots(slot1: 'TimeSlot', slot2: 'TimeSlot') -> 'TimeSlot':
        # İki slotu birleştirip yeni slot döndürür
```

**Slot Birleştirme (YENİ ⭐):**
Uzun sınavlar (4-8+ saat) için ardışık slotlar birleştirilebilir:
- 2 slot → 4 saat (09:00-13:30)
- 3 slot → 6 saat (09:00-16:00)
- 4 slot → 8 saat (09:00-18:30)
- 8+ saat → Gün başından başlayan dinamik slot (gereken süre kadar uzar)

#### `ScheduleSlot` - Planlama Slotu
```python
@dataclass
class ScheduleSlot:
    exam_date: date
    time_slot: TimeSlot
    classroom: Classroom
    is_available: bool = True
```

### Varsayılan Zaman Slotları

```python
DEFAULT_TIME_SLOTS = [
    TimeSlot(time(9, 0), time(11, 0)),    # 09:00 - 11:00 (120 dk)
    TimeSlot(time(11, 30), time(13, 30)), # 11:30 - 13:30 (120 dk)
    TimeSlot(time(14, 0), time(16, 0)),   # 14:00 - 16:00 (120 dk)
    TimeSlot(time(16, 30), time(18, 30)), # 16:30 - 18:30 (120 dk)
]
```

### Ana Metot: `generate_schedule()`

```python
def generate_schedule(self, start_date: str, end_date: str, 
                     department_id: Optional[int] = None,
                     exam_type: str = "final",
                     clear_existing: bool = False) -> Dict
```

#### Algoritma Akışı

```
┌─────────────────────────────────────────────────────────────┐
│                    1. Tarih Validasyonu                      │
│  - YYYY-MM-DD format kontrolü                                │
│  - Başlangıç <= Bitiş kontrolü                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 2. Mevcut Sınavları Temizle                  │
│  - clear_existing = True ise 'planned' durumundakileri sil   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               3. Planlanacak Dersleri Getir                  │
│  - _get_unscheduled_courses()                                │
│  - Sadece has_exam = True olan dersler                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               4. Dersleri Sırala (Greedy)                    │
│  - Önce öğrenci sayısına göre (azalan)                       │
│  - Sonra sınav süresine göre (azalan)                        │
│  purpose: En zor dersler önce planlansın                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               5. Derslikleri Getir ve Sırala                 │
│  - Kapasiteye göre azalan                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            6. Hafta İçi Günleri Oluştur                      │
│  - _get_weekdays_in_range(start, end)                       │
│  - Sadece Pazartesi-Cuma                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              7. Her Ders İçin Slot Ara                       │
│  - _schedule_course() çağrılır                              │
│  - Başarılı -> scheduled[]                                   │
│  - Başarısız -> failed[]                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  8. İstatistikleri Hesapla                    │
│  - _calculate_statistics()                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌──────────────��──────────────────────────────────────────────┐
│                    9. Sonuç Döndür                           │
│  - success, scheduled_count, failed_count                   │
│  - failed_courses (detaylı nedenleriyle)                     │
│  - schedule (planlanan sınavlar)                             │
│  - statistics                                               │
└─────────────────────────────────────────────────────────────┘
```

### `_schedule_course()` - Ders Planlama

**Parametreler:**
- `course`: Planlanacak ders
- `classrooms`: Tüm derslikler
- `dates`: Müsait tarihler
- `exam_type`: Sınav türü

**Adımlar:**

1. **Ders Tekrarı Kontrolü**
```python
existing_exams = self.exam_repo.get_by_course_id(course.id)
active_exams = [e for e in existing_exams if e.status != 'cancelled' and e.exam_type == exam_type]
if active_exams:
    return {'success': False, 'reason': "Bu ders için zaten bir final sınavı planlanmış"}
```

2. **Hoca Müsait Günlerini Filtrele**
```python
available_days = self._get_lecturer_available_days(lecturer_id)
available_exam_dates = []
for exam_date in dates:
    day_name = self._get_day_name(exam_date)
    if day_name in available_days:
        available_exam_dates.append(exam_date)
```

3. **Uygun Derslikleri Bul (Oda Tipi Filtreleme ile)** ⭐
```python
required_room_type = getattr(course, 'required_room_type', 'ANY') or 'ANY'
required_room_type = 'ANY' if required_room_type == 'STANDART' else required_room_type
filtered_classrooms = filter_classrooms_by_type(classrooms, required_room_type)
suitable_classrooms = [c for c in filtered_classrooms if c.capacity >= student_count]
```

4. **Çakışma Kontrolü ve Slot Atama (Uzun Sınav Desteği)** ⭐
```python
# Sınav süresine uygun slotları al
exam_slots = get_time_slots_for_duration(course.exam_duration)

for exam_date in available_exam_dates:
    for time_slot in exam_slots:  # Artık birleştirilmiş slotlar da var
        for classroom in suitable_classrooms:
            conflict = self._check_all_conflicts(...)
            if not conflict['has_conflict']:
                # Sınavı oluştur ve kaydet
                return {'success': True, 'exam': exam}
```

**Yeni Eklenen Kontroller:**
- Dersin gerektirdiği oda tipine göre derslik filtreleme
- Uzun sınavlar için birleştirilmiş slot kullanımı
- 8+ saat sınavlar için dinamik slot oluşturma
- Öğrenci bazlı çakışma kontrolü (student_courses) opsiyonel kullanım
- Oda tipi uyuşmazlığı durumunda hata mesajı

### `_try_combine_classrooms()` - Derslik Birleştirme

Büyük sınıflar için birden fazla dersliğin birleştirilmesi mantığı.

**Mantık:**
1. Derslikleri kapasiteye göre sırala
2. Her slot için müsait derslikleri topla
3. `_select_nearby_classrooms()` ile ana derslik + komşular + blok + kapasiteye göre tamamla
4. Toplam kapasite yeterliyse birleşik sınav kayıtlarını oluştur

```python
# Birleşik derslik notu
notes_text = f"Otomatik planlandı (Yakın Birleşik Derslikler: {combined_names})"

# Her ek derslik için
for i, additional_classroom in enumerate(selected_classrooms[1:], start=2):
    notes = f"Birleşik sınav ({i}/{len(selected_classrooms)}) - Ana derslik: {primary_name} - {notes_text}"
```

### Çakışma Kontrolü Metotları

#### `_check_all_conflicts()`
```python
def _check_all_conflicts(self, course_id, classroom_id, exam_date, 
                        start_time, end_time, department_id, 
                        course_year, lecturer_id) -> Dict:
```

**Kontroller:**
1. Derslik çakışması (`_has_classroom_conflict`)
2. Öğrenci çakışması (`_has_student_conflict`)
3. Hoca çakışması (`_has_lecturer_conflict`)

#### `_has_classroom_conflict()`
```python
# Aynı derslikte, aynı günde, çakışan saatte başka sınav var mı?
existing_exams = self.exam_repo.get_by_classroom_and_date(classroom_id, exam_date)
for exam in existing_exams:
    if self._times_overlap(start_time, end_time, exam.start_time, exam.end_time):
        return True
```

#### `_has_student_conflict()`
```python
if self.use_student_based_conflict and course_id:
    return self._has_student_conflict_based_on_students(
        course_id, exam_date, start_time, end_time
    )

# Eski sistem (bölüm/yıl bazlı)
existing_exams = self.exam_repo.get_by_department_and_date(department_id, exam_date)
# saat çakışması + year eşleşmesi kontrolü
```

#### `_has_student_conflict_based_on_students()`
```python
students_of_course = self._get_students_for_course(course_id)
if not students_of_course:
    return False  # öğrenci verisi yoksa çakışma bloklanmaz

existing_exams = self.exam_repo.get_by_date(exam_date)
for exam in existing_exams:
    if self._times_overlap(start_time, end_time, exam.start_time, exam.end_time):
        if students_of_course & self._get_students_for_course(exam.course_id):
            return True
```

#### `_has_lecturer_conflict()`
```python
# Hoca başka bir sınava girecek mi?
existing_exams = self.exam_repo.get_by_lecturer_and_date(lecturer_id, exam_date)
for exam in existing_exams:
    if self._times_overlap(start_time, end_time, exam.start_time, exam.end_time):
        return True
```

### `_times_overlap()` - Zaman Çakışması Kontrolü

```python
def _times_overlap(self, start1, end1, start2, end2) -> bool:
    # İki zaman aralığı çakışıyor mu?
    return not (end1 <= start2 or start1 >= end2)
```

### Yardımcı Metotlar

| Metot | Açıklama |
|-------|----------|
| `_get_day_name(exam_date)` | Tarihden gün adı alır |
| `_get_weekdays_in_range(start, end)` | Hafta içi günleri listeler |
| `_get_lecturer_available_days(lecturer_id)` | Hoca müsait günlerini alır |
| `_calculate_end_time(start_time, duration)` | Bitiş saatini hesaplar |
| `_calculate_statistics(scheduled, dates, classrooms)` | Planlama istatistikleri |
| `_has_student_conflict_based_on_students(course_id, ...)` | Öğrenci ID kesişimi ile çakışma kontrolü |
| `_get_students_for_course(course_id)` | Dersin öğrenci ID kümesini (cache) döndürür |
| `clear_student_cache()` | Öğrenci cache'ini temizler |
| `_exam_to_dict(exam)` | Sınav nesnesini sözlüğe çevirir |
| `_get_unscheduled_courses(dept_id, exam_type)` | Planlanmamış dersleri alır |
| `get_time_slots_for_duration(duration)` | YENİ: Belirli süre için uygun slotları döndürür |
| `_generate_combined_slots(duration)` | YENİ: Uzun sınavlar için birleştirilmiş slotlar oluşturur |
| `filter_classrooms_by_type(classrooms, type)` | YENİ: Derslikleri oda tipine göre filtreler |
| `_select_nearby_classrooms(classrooms, capacity)` | Yakın derslikleri seçer (komşu/blok/kapasite) |
| `validate_manual_schedule(...)` | Manuel planlama için validasyon/uyarı listesi |
| `clear_schedule(start_date, end_date)` | Planlanan sınavları siler |
| `get_schedule_statistics(start_date, end_date)` | Genel sınav istatistiklerini döndürür |
| `set_time_slots(slots)` | Zaman slotlarını özelleştirir |
| `reset_time_slots()` | Varsayılan slotlara döner |

### İstatistik Hesaplama

```python
def _calculate_statistics(self, scheduled, exam_dates, classrooms) -> Dict:
    return {
        'total_exams': len(scheduled),
        'total_students': total_students,
        'exams_by_date': {...},        # Tarihe göre sınav sayısı
        'exams_by_classroom': {...},   # Dersliğe göre sınav sayısı
        'utilization_rate': 42.5       # (gün x slot x derslik) üzerinden %
    }
```

### Başarı Durumları

| Durum | Mesaj |
|-------|-------|
| Tam başarı | `"Tüm dersler (X) başarıyla planlandı."` |
| Kısmi başarı | `"X sınav planlandı, Y sınav planlanamadı."` |
| Tam başarısız | `"Hiçbir ders planlanamadı. Y ders için uygun slot bulunamadı."` |

### Hata Nedenleri

| Neden | Açıklama |
|-------|----------|
| `"Geçersiz tarih formatı"` | YYYY-MM-DD formatı beklenir |
| `"Başlangıç tarihi bitiş tarihinden sonra olamaz"` | Tarih mantık hatası |
| `"Aktif derslik bulunamadı"` | Hiç derslik yok |
| `"Hafta içi gün bulunamadı"` | Tarih aralığında Pazartesi-Cuma yok |
| `"Öğretim üyesi belirtilen tarih aralığında müsait değil"` | Hoca müsait değil |
| `"Sınav süresi (...) için uygun zaman bloğu bulunamadı"` | Süre, mevcut slotların üstünde |
| `"Yeterli kapasiteli derslik bulunamadı"` | Kapasite sorunu |
| `"Yakın derslikler birleştirilerek de yeterli kapasite sağlanamadı"` | Birleştirme denemeleri başarısız |
| `"Tüm slotlar dolu"` | Tüm kombinasyonlar denendi, uygun slot yok |
| `"Yeterli kapasiteli {room_type} derslik bulunamadı"` | YENİ: Oda tipi uyuşmazlığı |
| `"Uygun zaman dilimi bulunamadı"` | YENİ: Uzun sınav için slot birleştirilemedi |

---

## Olası Hatalar ve Çözümler

### 1. Transaction Sorunu
⚠️ **Sorun:** Çoklu derslik sınav oluşturmada kısmi kayıt riski.
```python
# Ana derslik kaydedildi
primary_id = self.exam_repo.create(exam)

# Hata oluşursa burada...
for i, additional_classroom in enumerate(classroom_ids[1:]):
    self.exam_repo.create(additional_exam)  # Burası başarısız olabilir
```
**Çözüm:** Database transaction kullanımı.

### 2. Email Çakışma Döngüsü
⚠️ **Sorun:** Sonsuz döngü riski.
```python
while existing:
    email = base_email.replace('@', f'{counter}@')
    counter += 1
    existing = self.repository.get_by_email(email)
```
**Çözüm:** Maksimum deneme sayısı sınırlaması eklenmeli.

### 3. Period Hesaplama
⚠️ **Sorun:** Period dışında değerler için varsayılan kullanılıyor.
```python
if period not in [1, 2, 3, 4, 5, 6, 7, 8]:
    # Uyarı veya hata verilmeli
```

### 4. Scheduler Performans
⚠️ **Sorun:** Büyük veri setlerinde performans sorunu.
```python
# Üçlü döngü: O(dersler × günler × slotlar × derslikler)
for exam_date in available_exam_dates:
    for time_slot in self.time_slots:
        for classroom in suitable_classrooms:
```
**Çözüm:** Optimization veya farklı algoritma (Genetic Algorithm, Constraint Programming).

### 5. Null Kontrol Eksikliği
```python
student_count = course.student_count or 0  # 0 olabilir
exam_duration = course.exam_duration or 60  # Varsayılan değer
```

---

## Validasyon Özeti

| Validasyon | Servis | Kritiklik |
|------------|--------|-----------|
| Şifre uzunluğu | AuthService | 🟡 Orta |
| Şifre hash türü | AuthService | 🔴 Yüksek (SHA256) |
| Kod benzersizliği | Faculty, Department, Course, Lecturer | 🟢 Normal |
| Kapasite kontrolü | Classroom, Course | 🟢 Normal |
| Zaman çakışması | ExamSchedule, Scheduler | 🔴 Kritik |
| Öğrenci çakışması | ExamSchedule, Scheduler | 🔴 Kritik |
| Hoca çakışması | ExamSchedule, Scheduler | 🔴 Kritik |
| Derslik uygunluğu | ExamSchedule, Scheduler | 🟡 Orta |
| Müsait gün kontrolü | Scheduler | 🟡 Orta |

---

## Service Bağımlılıkları

```
AuthService
└── UserRepository

FacultyService
└── FacultyRepository

DepartmentService
└── DepartmentRepository

LecturerService
└── LecturerRepository

CourseService
└── CourseRepository

ClassroomService
└── ClassroomRepository

ExamScheduleService
├── ExamScheduleRepository
├── CourseRepository
├── ClassroomRepository
└── LecturerRepository

SchedulerService (En karmaşık)
├── CourseRepository
├── ClassroomRepository
├── ExamScheduleRepository
├── LecturerRepository
└── DepartmentRepository
```

---

## 9. StudentImportService - Öğrenci İçe Aktarma Servisi ⭐ YENİ

**Dosya:** [`src/services/student_import_service.py`](../src/services/student_import_service.py)

### Amaç
Excel dosyalarından öğrenci listelerini okuyup veritabanına kaydeder. StudentImporter sınıfı için yüksek seviyeli bir arayüz sağlar.

### Özellikler

| Özellik | Açıklama |
|---------|----------|
| Excel Okuma | `.xls` ve `.xlsx` dosya formatları desteklenir |
| Auto Kolon Tespiti | Farklı Excel formatları için esnek kolon eşleştirme |
| Batch Import | Tüm bir klasördeki dosyaları toplu içe aktarma |
| Özet Raporlama | Başarılı/başarısız import istatistikleri |
| Validasyon | Ders varlığı kontrolü ve doğrulama |

### Metotlar

#### `import_from_excel()` - Tek Dosyadan İçe Aktarma

```python
def import_from_excel(
    file_path: str,
    course_id: Optional[int] = None,
    course_code: Optional[str] = None,
    department_id: Optional[int] = None,
    semester: Optional[str] = None,
    year: Optional[int] = None
) -> ImportResult
```

**Dönüş Değeri (ImportResult):**
```python
{
    'success': bool,
    'file_name': str,
    'course_code': str,
    'students_imported': int,
    'student_courses_created': int,
    'error': str | None
}
```

#### `import_from_excel_directory()` - Klasörden Toplu İçe Aktarma

Belirtilen klasördeki tüm Excel dosyalarını içe aktarır.

#### `get_import_summary()` - İçe Aktarma Özeti

İçe aktarma sonuçlarının istatistiksel özetini döndürür:

```python
{
    'total_files': 12,
    'successful_files': 10,
    'failed_files': 2,
    'total_students_imported': 450,
    'success_rate': 83.33
}
```

### Bağımlılıklar

```
StudentImportService
├── StudentImporter (utils)
│   └── StudentRepository
├── CourseRepository
└── DepartmentRepository
```

---

## Öneriler

1. **Transaction Yönetimi:** Çoklu kayıt işlemlerinde transaction kullanın
2. **Logging:** Hata durumlarında detaylı loglama ekleyin
3. **Caching:** Sık kullanılan verileri cache'leyin (fakülteler, bölümler)
4. **Batch Processing:** Scheduler'da toplu işleme ekleyin
5. **Validation Framework:** Marshmallow veya Pydantic kullanın
6. **Rate Limiting:** Otomatik planlama için rate limiting ekleyin
7. **Notification:** Sınav planlandığında bildirim gönderin
8. **Retry Logic:** Geçici hatalar için retry mekanizması
9. **Progress Tracking:** Scheduler için ilerleme takibi
10. **Cancellation:** Çalışan planlama işlemini iptal etme özelliği
