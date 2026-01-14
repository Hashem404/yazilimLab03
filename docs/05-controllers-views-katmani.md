# Controllers ve Views Katmanı Dokümantasyonu

Bu belge, projedeki Controller ve View katmanlarının yapılarını, UI akışını ve olası hatalarını detaylandırmaktadır.

## 📁 Katman Yapısı

```
src/
├── controllers/
│   ├── __init__.py
│   ├── auth_controller.py      # Kimlik doğrulama controller
│   ├── dashboard_controller.py # Ana panel controller (701 satır)
│   └── export_controller.py    # Dışa aktarma controller
│
└── views/
    ├── __init__.py
    ├── login_view.py           # Giriş ekranı
    ├── dashboard_view.py       # Ana panel view (403 satır)
    ├── base_crud_view.py       # CRUD taban sınıfı (611 satır)
    ├── faculty_view.py         # Fakülte yönetimi
    ├── department_view.py      # Bölüm yönetimi
    ├── lecturer_view.py        # Öğretim üyesi yönetimi
    ├── course_view.py          # Ders yönetimi
    ├── classroom_view.py       # Derslik yönetimi
    ├── exam_schedule_view.py   # Sınav programı yönetimi
    ├── import_view.py          # Veri içe aktarma (Öğrenci Excel import) ⭐
    ├── reports_view.py         # Raporlama
    ├── student_schedule_view.py # Öğrenci programı
    └── components/
        ├── __init__.py
        ├── sidebar.py          # Sol menü bileşeni
        ├── data_table.py       # Veri tablosu bileşeni
        └── form_dialog.py      # Form dialog bileşeni (505 satır)
```

---

## 1. Controller Katmanı

Controller katmanı, View ile Service arasındaki köprü görevi görür. UI'dan gelen istekleri alır, Service katmanına yönlendirir ve sonuçları View'a döndürür.

### 1.1 AuthController - Kimlik Doğrulama Controller

**Dosya:** [`src/controllers/auth_controller.py`](../src/controllers/auth_controller.py)

#### Amaç
Kullanıcı girişi, çıkışı ve yetki kontrolü işlemlerini yönetir.

#### Yapı

```python
class AuthController:
    def __init__(self, view: Any = None):
        self.auth_service = AuthService()
        self.view = view
        self.current_user: Optional[dict] = None
        self._on_login_success: Optional[Callable] = None
        self._on_logout: Optional[Callable] = None
```

#### Metotlar

| Metot | Açıklama | Dönüş |
|-------|----------|-------|
| `login(username, password)` | Kullanıcı girişi | `{'success', 'message', 'user'}` |
| `logout()` | Kullanıcı çıkışı | `{'success', 'message'}` |
| `is_authenticated()` | Oturum kontrolü | `bool` |
| `has_permission(permission)` | İzin kontrolü | `bool` |
| `has_role(role)` | Rol kontrolü | `bool` |
| `change_password(old, new)` | Şifre değiştirme | `{'success', 'message'}` |
| `get_current_user()` | Mevcut kullanıcı | `dict` or `None` |
| `get_user_department_id()` | Kullanıcı bölümü | `int` or `None` |

#### Callback Yapısı

```python
def set_login_callback(self, callback: Callable) -> None:
    self._on_login_success = callback

def set_logout_callback(self, callback: Callable) -> None:
    self._on_logout = callback
```

#### Kullanım Örneği

```python
# Login işlemi
result = auth_controller.login("admin", "password")
if result['success']:
    user_info = result['user']
    # user_info: {'id', 'username', 'full_name', 'email', 'role', 'department_id',
    #             'student_id', 'student_number'}  # Öğrenci için ek bilgiler
    #             'lecturer_id'}                    # Hoca için ek bilgi

# Rol kontrolü
if auth_controller.is_admin():
    # Admin işlemleri
    pass
```

---

### 1.2 DashboardController - Ana Panel Controller

**Dosya:** [`src/controllers/dashboard_controller.py`](../src/controllers/dashboard_controller.py) - **701 satır**

#### Amaç
T��m entity'ler (Fakülte, Bölüm, Derslik, Öğretim Üyesi, Ders, Sınav) için CRUD operasyonlarını yönetir.

#### Yapı

```python
class DashboardController:
    def __init__(self, view: Any = None):
        self.view = view
        self.faculty_service = FacultyService()
        self.department_service = DepartmentService()
        self.classroom_service = ClassroomService()
        self.lecturer_service = LecturerService()
        self.course_service = CourseService()
        self.exam_service = ExamScheduleService()
        self.scheduler_service = SchedulerService()
```

#### Dashboard Metotları

##### `get_dashboard_stats()` - Sistem İstatistikleri

```python
def get_dashboard_stats(self) -> Dict[str, Any]:
    return {
        'total_faculties': ...,      # Toplam fakülte sayısı
        'total_departments': ...,    # Toplam bölüm sayısı
        'total_classrooms': ...,     # Toplam derslik sayısı
        'total_lecturers': ...,      # Toplam öğretim üyesi sayısı
        'total_courses': ...,        # Toplam ders sayısı
        'total_exams': ...,          # Toplam sınav sayısı
        'this_week_exams': ...,      # Bu haftaki sınavlar
        'pending_exams': ...,        # Bekleyen sınavlar (planned)
        'today_exams': ...           # Bugünkü sınavlar
    }
```

##### `get_upcoming_exams(days)` - Yaklaşan Sınavlar

```python
def get_upcoming_exams(self, days: int = 7) -> List[Dict]:
    # Belirtilen gün sayısı içindeki sınavları döndürür
    # Tarih ve saate göre sıralı
```

##### `get_classroom_utilization(exam_date)` - Derslik Kullanım Oranı

```python
def get_classroom_utilization(self, exam_date: date) -> Dict[str, Any]:
    # Belirtilen tarihte derslik kullanım oranlarını hesaplar
    # Zaman slotlarına göre kullanım analizi
    return {
        '09:00-10:30': {
            'used_classrooms': 5,
            'total_classrooms': 10,
            'used_capacity': 300,
            'total_capacity': 500,
            'percentage': 60.0
        },
        ...
    }
```

##### `generate_auto_schedule()` - Otomatik Planlama

```python
def generate_auto_schedule(self, start_date, end_date, 
                          department_id=None, exam_type="final") -> Dict:
    # SchedulerService.generate_schedule() çağrır
    result = self.scheduler_service.generate_schedule(...)
    return result
```

##### `get_schedule_conflicts()` - Program Çakışmaları

```python
def get_schedule_conflicts(self, start_date, end_date) -> List[Dict]:
    # Belirtilen tarih aralığındaki çakışmaları tespit eder
    return [
        {
            'type': 'classroom_conflict',
            'date': '2025-01-15',
            'time': '09:00-11:00',
            'classroom': 'A-101',
            'course1': 'CS101',
            'course2': 'MATH101'
        },
        ...
    ]
```

#### CRUD Operasyonları

Her entity için standart CRUD metotları:

| Metot | Açıklama | Parametre |
|-------|----------|-----------|
| `get_all_*()` | Tümünü listele | - |
| `get_*_by_*()` | Filtreleme | ID/faculty_id/department_id |
| `create_*()` | Yeni kayıt | `data: dict` |
| `update_*()` | Kayıt güncelle | `id, data: dict` |
| `delete_*()` | Kayıt sil | `id` |

**Örnek - Fakülte CRUD:**

```python
# Listele
faculties = controller.get_all_faculties()

# Oluştur
result = controller.create_faculty({
    'name': 'Mühendislik Fakültesi',
    'code': 'MUF',
    'dean_name': 'Prof. Dr. Ahmet Yılmaz'
})
# result: {'success', 'data' (id), 'message'}

# Güncelle
result = controller.update_faculty(1, {
    'name': 'Yeni Ad',
    'code': 'YENI',
    'dean_name': 'Yeni Dekan'
})

# Sil
result = controller.delete_faculty(1)
```

#### Ders CRUD Detayları

```python
def create_course(self, data: dict) -> dict:
    success, message, course_id = self.course_service.create(
        department_id=data.get('department_id'),
        lecturer_id=data.get('lecturer_id'),
        code=data.get('code', ''),
        name=data.get('name', ''),
        credit=int(data.get('credit', 3)),
        year=int(data.get('year', 1)),
        semester=int(data.get('semester', 1)),
        student_count=int(data.get('student_count', 0)),
        lecturer_count=int(data.get('lecturer_count', 1)),
        exam_type=data.get('exam_type', 'Yazılı'),
        exam_duration=int(data.get('exam_duration', 60)),
        has_exam=bool(data.get('has_exam', True)),
        period=int(data.get('period', 1)) if data.get('period') else None,
        theory_hours=int(data.get('theory_hours', 0)),
        lab_hours=int(data.get('lab_hours', 0)),
        course_type=data.get('course_type', 'Zorunlu'),
        description=data.get('description', '')
    )
```

#### Olası Hatalar

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| `'success': False` | Validasyon hatası | `result['message']` kontrol edilmeli |
| `KeyError` | `data.get()` eksik parametre | Varsayılan değerler kullanılmalı |
| `ValueError` | Tür dönüşümü hatası | Try-except bloğu eklenmeli |

---

### 1.3 ExportController - Dışa Aktarma Controller

**Dosya:** [`src/controllers/export_controller.py`](../src/controllers/export_controller.py)

#### Amaç
Sınav programını Excel formatında dışa aktarır.

#### Metotlar

##### `export_exam_schedule_to_excel()`

```python
def export_exam_schedule_to_excel(self, start_date: date, end_date: date,
                                  output_path: str = None) -> tuple:
    # Dönüş: (success, message, file_path)
```

**Özellikler:**
- `openpyxl` kütüphanesi kullanır
- Formatlı başlık satırı (koyu mavi arka plan, beyaz yazı)
- Otomatik sütun genişlikleri
- Sınav türü ve durum etiketleri (Türkçe)

**Başlıklar:**
| Tarih | Saat | Ders Kodu | Ders Adı | Öğretim Görevlisi | Derslik | Öğrenci Sayısı | Sınav Türü | Durum |

**Hata Durumları:**
- `ImportError`: `openpyxl` kurulu değil
- `False`: Geçersiz dosya yolu veya uzantısı
- `False`: Sınav bulunamadı

##### `_get_exam_type_label()` - Sınav Türü Etiketi

```python
labels = {
    'midterm': 'Vize',
    'final': 'Final',
    'makeup': 'Bütünleme',
    'quiz': 'Quiz'
}
```

##### `_get_status_label()` - Durum Etiketi

```python
labels = {
    'planned': 'Planlandı',
    'confirmed': 'Onaylandı',
    'cancelled': 'İptal Edildi'
}
```

---

## 2. View Katmanı

View katmanı, Tkinter tabanlı GUI uygulamalarının kullanıcı arayüzünü oluşturur.

### 2.1 LoginView - Giriş Ekranı

**Dosya:** [`src/views/login_view.py`](../src/views/login_view.py) - **267 satır**

#### Amaç
Kullanıcı giriş formunu gösterir ve kimlik doğrulamasını yönetir.

#### Renk Paleti

```python
COLORS = {
    'primary': '#3498db',        # Mavi - Butonlar
    'primary_dark': '#2980b9',   # Koyu mavi - Hover
    'secondary': '#2c3e50',      # Koyu gri - Başlıklar
    'background': '#ecf0f1',     # Açık gri - Arka plan
    'card_bg': '#ffffff',        # Beyaz - Kart
    'text': '#2c3e50',           # Koyu gri - Metin
    'text_light': '#7f8c8d',     # Gri - Alt metin
    'error': '#e74c3c',          # Kırmızı - Hata
    'success': '#27ae60',        # Yeşil - Başarı
}
```

#### Yapı

```
┌─────────────────────────────────────┐
│           🎓 (Logo)                 │
│    Üniversite Sınav Programı        │
│       Sınav Yönetim Sistemi         │
│                                     │
│  Kullanıcı Adı                     │
│  [___________________]              │
│                                     │
│  Şifre                             │
│  [___________________]              │
│                                     │
│  ⚠ Hata mesajı                     │
│                                     │
│     [ Giriş Yap ]                  │
│                                     │
│  © 2025 Üniversite...              │
└─────────────────────────────────────┘
```

#### Metotlar

| Metot | Açıklama |
|-------|----------|
| `_create_widgets()` | UI bileşenlerini oluşturur |
| `_setup_bindings()` | Klavye kısayolları (Enter, odak) |
| `_on_login_click()` | Giriş butonu tıklama |
| `_show_error(message)` | Hata mesajı göster |
| `_clear_error()` | Hata mesajını temizle |
| `_open_student_schedule(user_info)` | Öğrenci için program aç |

#### Öğrenci Yönlendirme

```python
def _on_login_click(self):
    # ...
    if success:
        role = (user_info.get('role') or user_info.get('user_type') or '').lower()
        if role in ('student', 'ogrenci'):
            self._open_student_schedule(user_info)  # Doğrudan öğrenci programı
            return
```

---

### 2.2 DashboardView - Ana Panel

**Dosya:** [`src/views/dashboard_view.py`](../src/views/dashboard_view.py) - **403 satır**

#### Amaç
Uygulamanın ana ekranını yönetir. Sol menü ve içerik alanından oluşur.

#### Yapı

```
┌─────────────┬──────────────────────────────────┐
│  📋 Menü    │       İçerik Alanı              │
│             │                                  │
│  🏠 Ana     │  [Rol bazlı içerik]             │
│  🏢 Fak.    │                                  │
│  📚 Bölüm   │  - Admin: Tüm istatistikler      │
│  👨‍🏫 Hoca   │  - Bölüm Yetkili: Bölüm datası  │
│  📅 Prog.   │  - Hoca: Sınav programı         │
│             │  - Öğrenci: Sınav programı      │
│             │                                  │
│  👤 User    │                                  │
│  🚪 Çıkış   │                                  │
└─────────────┴──────────────────────────────────┘
```

#### Rol Bazlı Ana Sayfalar (Kişiselleştirilmiş Görünüm) ⭐

| Rol | Metot | Gösterilen İçerik | Filtreleme Mantığı |
|-----|-------|-------------------|-------------------|
| `admin` | `_show_admin_home()` | Tüm sistem istatistikleri | Tüm sınavlar |
| `bolum_yetkilisi` | `_show_bolum_yetkilisi_home()` | Bölüm istatistikleri | Kendi bölümünün sınavları |
| `hoca` | `_show_hoca_home()` | Kişiselleştirilmiş sınav programı | **Sadece verdiği derslerin sınavları** |
| `ogrenci` | `_show_ogrenci_home()` | Kişiselleştirilmiş sınav programı | **Sadece aldığı derslerin sınavları** |

**Önemli Değişiklik:**
- Hoca ve öğrenci artık sadece kendi derslerinin/aldığı derslerin sınavlarını görür
- Filtreleme [`filter_schedule_by_user()`](#kullanıcı-bazlı-filtreleme) metodu ile yapılır

#### İstatistik Kartları (Admin)

```python
stats = [
    ('🏛️ Fakülteler', count, '#3498db'),
    ('📚 Bölümler', count, '#9b59b6'),
    ('🚪 Derslikler', count, '#1abc9c'),
    ('👨‍🏫 Öğretim Üyeleri', count, '#e67e22'),
    ('📖 Dersler', count, '#e74c3c'),
    ('📅 Planlanan Sınavlar', count, '#2ecc71'),
]
```

#### Menü Tıklama İşleme

```python
def _on_menu_click(self, key, view_name):
    # Mevcut içerik alanını temizle
    for widget in self.content_frame.winfo_children():
        widget.destroy()
    
    # Rol kontrolü ve view yükleme
    if key == 'faculties':
        if self.user_role == 'admin':
            from src.views.faculty_view import FacultyView
            self.current_view = FacultyView(self.content_frame, self)
    elif key == 'schedule':
        from src.views.exam_schedule_view import ExamScheduleView
        self.current_view = ExamScheduleView(self.content_frame, self)
    # ...
```

---

### 2.3 BaseCrudView - CRUD Taban Sınıfı

**Dosya:** [`src/views/base_crud_view.py`](../src/views/base_crud_view.py) - **611 satır**

#### Amaç
Tüm CRUD ekranları için ortak yapı sağlar. Alt sınıflar bu sınıfı extend eder.

#### Üzerinden Gelecek Metotlar

| Metot | Açıklama |
|-------|----------|
| `load_data(search_term)` | Verileri yükler |
| `get_form_fields()` | Form alanlarını tanımlar |
| `validate_form(data)` | Form validasyonu |
| `create_item(data)` | Yeni kayıt oluşturur |
| `update_item(id, data)` | Kayıt günceller |
| `delete_item(id)` | Kayıt siler |

#### UI Yapısı

```
┌────────────────────────────────────────────────┐
│  Başlık              [➕ Ekle] [✏️] [🗑️] [🔄]   │
├──────────────────────��─────────────────────────┤
│  🔍 [_______________] [✖]                      │
├────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐ │
│  │  ID │ Ad       │ Soyad    │ ...         │ │
│  ├──────────────────────────────────────────┤ │
│  │   1 │ Ahmet    │ Yılmaz   │ ...         │ │
│  │   2 │ Mehmet   │ Demir    │ ...         │ │
│  │   3 │ Ayşe     │ Kaya     │ ...         │ │
│  └──────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
```

#### Header Oluşturma

```python
def _create_header(self):
    # Başlık etiketi
    # Butonlar: Ekle, Düzenle, Sil, Yenile
    # Her buton için hover efekti
```

#### Arama Çubuğu

```python
def _create_search_bar(self):
    # 🔍 ikonu
    # Arama inputu
    # Temizle butonu
    # Gerçek zamanlı arama (trace)
```

#### CRUD İşlem Akışı

```
[Ekle] → _on_add() → _show_form_dialog(mode='add')
         ↓
      FormDialog açılır
         ↓
      _save_form() → validate_form() → create_item()
         ↓
      Başarılı → load_data() → Tablo yenilenir

[Düzenle] → _on_edit() → _show_form_dialog(mode='edit', data=selected)
         ↓
      FormDialog (mevcut verilerle)
         ↓
      _save_form() → validate_form() → update_item()

[Sil] → _on_delete() → ConfirmDialog → delete_item()
```

---

### 2.4 ExamScheduleView - Sınav Programı Yönetimi

**Dosya:** [`src/views/exam_schedule_view.py`](../src/views/exam_schedule_view.py) - **771 satır**

#### Amaç
Sınav programını listeler; role göre görüntüleme/CRUD, otomatik planlama ve toplu silme aksiyonlarını yönetir.

#### Rol Bazlı Davranış
- `hoca` ve `ogrenci`: `view_only` mod (Ekle/Düzenle/Sil butonları gizlenir)
- `admin`: Toplu silme ve otomatik planlama butonları, çoklu seçim

#### Öne Çıkanlar
- `_format_classrooms()` birleşik derslikleri ` + ` ile tek hücrede gösterir
- `AutoScheduleDialog`: tarih aralığı + bölüm (opsiyonel) + sınav türü seçimi
- Durum seçenekleri: `planned`, `confirmed`, `completed`, `cancelled`

#### Durum Notları
- PDF/Excel dışa aktarma butonları mevcut; `export_schedule_pdf` ve `export_schedule_excel` controller metotları TODO olduğu için hata yakalanıyor

---

## 3. Component Bileşenleri

### 3.1 Sidebar - Sol Menü

**Dosya:** [`src/views/components/sidebar.py`](../src/views/components/sidebar.py) - **104 satır**

#### Rol Bazlı Menü Yapısı

```python
MENU_ITEMS_BY_ROLE = {
    'admin': [
        ('dashboard', '🏠 Ana Sayfa', 'DashboardView'),
        ('faculties', '🏢 Fakülteler', 'FacultyView'),
        ('departments', '📚 Bölümler', 'DepartmentView'),
        ('classrooms', '🚪 Derslikler', 'ClassroomView'),
        ('lecturers', '👨‍🏫 Öğretim Üyeleri', 'LecturerView'),
        ('courses', '📖 Dersler', 'CourseView'),
        ('import_view', 'Veri Yükleme', 'ImportView'),
        ('student_lists', 'Sınıf Listeleri', 'CourseView'),
        ('schedule', '📅 Sınav Programı', 'ExamScheduleView'),
        ('reports', '📊 Raporlar', 'ReportsView'),
    ],
    'bolum_yetkilisi': [
        ('dashboard', '🏠 Ana Sayfa', 'DashboardView'),
        ('lecturers', '👨‍🏫 Öğretim Üyeleri', 'LecturerView'),
        ('courses', '📖 Dersler', 'CourseView'),
        ('import_view', 'Veri Yükleme', 'ImportView'),
        ('student_lists', 'Sınıf Listeleri', 'CourseView'),
        ('schedule', '📅 Sınav Programı', 'ExamScheduleView'),
    ],
    'hoca': [
        ('dashboard', '🏠 Ana Sayfa', 'DashboardView'),
        ('schedule', '📅 Sınav Programı', 'ExamScheduleView'),
    ],
    'ogrenci': [
        ('dashboard', '🏠 Ana Sayfa', 'DashboardView'),
        ('schedule', '📅 Sınav Programı', 'ExamScheduleView'),
    ],
}
```

#### Rol Gösterim Adları

```python
role_names = {
    'admin': '👑 Admin',
    'bolum_yetkilisi': '🎓 Bölüm Yetkilisi',
    'hoca': '👨‍🏫 Öğretim Üyesi',
    'ogrenci': '👨‍🎓 Öğrenci'
}
```

---

### 3.2 DataTable - Veri Tablosu

**Dosya:** [`src/views/components/data_table.py`](../src/views/components/data_table.py) - **95 satır**

#### Amaç
Treeview tabanlı, kaydırılabilir veri tablosu bileşeni.

#### Yapı

```python
class DataTable(tk.Frame):
    def __init__(self, parent, columns: list, 
                 on_select=None, on_double_click=None, 
                 select_mode='browse'):
```

#### Kolon Tanımı

```python
columns = [
    ('id', 'ID', 50),
    ('name', 'Ad', 150),
    ('code', 'Kod', 100),
    ...
]
```

#### Metotlar

| Metot | Açıklama |
|-------|----------|
| `load_data(data)` | Tabloya veri yükler |
| `clear()` | Tabloyu temizler |
| `get_selected()` | Seçili satırı döndürür |
| `get_selected_id()` | Seçili satır ID'sini döndürür |
| `get_selected_all()` | Tüm seçili satırları döndürür (çoklu seçim) |
| `get_selected_ids()` | Seçili ID'leri döndürür |
| `get_selection_count()` | Seçili satır sayısı |

#### Seçim Modları

| Mod | Açıklama |
|------|----------|
| `'browse'` | Tek seçim |
| `'extended'` | Çoklu seçim (Ctrl/Shift) |

---

### 3.3 FormDialog - Form Dialog Bileşeni

**Dosya:** [`src/views/components/form_dialog.py`](../src/views/components/form_dialog.py) - **505 satır**

#### Amaç
Modal dialog penceresi ile ekleme/düzenleme formları gösterir.

#### Desteklenen Alan Türleri

| Tür | Açıklama |
|-----|----------|
| `entry` | Tek satırlı metin girişi |
| `spinbox` | Sayısal giriş (min-max arası) |
| `combobox` | Dropdown seçim |
| `combo` | ID-Value pair seçim |
| `multi_combo` | Çoklu seçim listesi |
| `text` | Çok satırlı metin |
| `checkbox` | Onay kutusu |
| `multi_checkbox` | Birden fazla onay kutusu |
| `date` | Tarih girişi (YYYY-MM-DD) |
| `time` | Saat girişi (HH:MM) |

#### Alan Tanımı Örneği

```python
fields = [
    {
        'name': 'first_name',
        'label': 'Ad',
        'type': 'entry',
        'required': True
    },
    {
        'name': 'department_id',
        'label': 'Bölüm',
        'type': 'combo',
        'required': True,
        'options': [(1, 'Bilgisayar Müh.'), (2, 'Yazılım Müh.')]
    },
    {
        'name': 'available_days',
        'label': 'Müsait Günler',
        'type': 'multi_checkbox',
        'options': ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma'],
        'default': ['Pazartesi', 'Çarşamba', 'Cuma']
    },
    {
        'name': 'capacity',
        'label': 'Kapasite',
        'type': 'spinbox',
        'from_': 10,
        'to': 200,
        'required': True
    }
]
```

#### Validasyon

```python
def _validate_fields(self) -> tuple[bool, str]:
    for field in self.fields:
        if required:
            if value is None or value == '':
                return False, f"'{field_label}' alanı zorunludur."
        
        if field_type == 'date':
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                return False, f"'{field_label}' YYYY-MM-DD formatında olmalıdır."
        
        if field_type == 'time':
            if not re.match(r'^\d{2}:\d{2}$', value):
                return False, f"'{field_label}' HH:MM formatında olmalıdır."
```

#### ConfirmDialog

```python
class ConfirmDialog(tk.Toplevel):
    # Evet/Hayır onay dialogu
    # Kullanım: result = dialog.show()  # True/False
```

---

## 4. UI Akışı

### 4.1 Uygulama Başlatma Akışı

```
main.py
   ↓
LoginView göster
   ↓
Kullanıcı girişi
   ↓
AuthController.login()
   ↓
Başarılı → DashboardView göster
   ↓
Rol bazlı menü ve içerik
```

### 4.2 CRUD İşlem Akışı

```
DashboardView (menu tıklama)
   ↓
BaseCrudView (örn. FacultyView)
   ↓
DataTable (veri listeleme)
   ↓
[Ekle] → FormDialog → validasyon → create_item()
[Düzenle] → FormDialog (mevcut veri) → update_item()
[Sil] → ConfirmDialog → delete_item()
   ↓
load_data() → tablo yenileme
```

### 4.3 Sınav Planlama Akışı

```
ExamScheduleView
   ↓
[Otomatik Planla] butonu
   ↓
Tarih aralığı seçimi
   ↓
DashboardController.generate_auto_schedule()
   ↓
SchedulerService.generate_schedule()
   ↓
Sonuç gösterimi (başarılı/başarısız dersler)
   ↓
DataTable güncelleme
```

### 4.4 Öğrenci Import Akışı ⭐ (Yeni)

```
DashboardView
   ↓
[Veri İçe Aktarma] menü seçimi
   ↓
ImportView göster
   ↓
[Öğrenci Import] sekmesi
   ↓
Excel dosyası seçimi
   ↓
Ders seçimi
   ↓
[İçe Aktar] butonu
   ↓
StudentImporter.import_from_excel()
   ↓
Sonuç gösterimi (eklenen öğrenci sayısı, hatalar)
```

---

## 5. ImportView - Veri İçe Aktarma Ekranı ⭐ (Yeni)

**Dosya:** [`src/views/import_view.py`](../src/views/import_view.py)

### Amaç
Excel dosyalarından öğrenci listelerini sisteme aktarır.

### UI Yapısı

```
┌────────────────────────────────────────────────────────────┐
│                  Veri İçe Aktarma                         │
├────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐ │
│  │  [Öğrenci Import]  [Diğer]                           │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  Excel Dosyası:                                           │
│  [Gözat...]  SınıfListesi[BLM111].xls                    │
│                                                            │
│  Ders:                                                    │
│  [BLM101 - Programlamaya Giriş ▼]                        │
│                                                            │
│  Dönem:                                                   │
│  [2024-2025 Güz]                                         │
│                                                            │
│  ⚙ Ayarlar:                                              │
│  ☐ İlk satır başlık                                       │
│  ☐ Mevcut öğrencileri güncelle                            │
│                                                            │
│     [ 📥 İçe Aktar ]                                      │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Sonuçlar:                                           │ │
│  │  ✅ 45 öğrenci eklendi                               │ │
│  │  ℹ️ 3 öğrenci zaten mevcuttu (güncellendi)            │ │
│  │  ❌ 2 satır atlandı (geçersiz veri)                   │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### Metotlar

| Metot | Açıklama |
|-------|----------|
| `_create_widgets()` | UI bileşenlerini oluşturur |
| `_browse_file()` | Excel dosyası seçme diyalogunu açar |
| `_load_courses()` | Ders listesini yükler |
| `_on_import_click()` | İçe aktarma işlemini başlatır |
| `_display_results()` | Sonuçları gösterir |

### Desteklenen Excel Formatları

| Format | Uzantı | Kütüphane |
|--------|--------|-----------|
| Legacy Excel | .xls | xlrd |
| Modern Excel | .xlsx | openpyxl |

### Excel Kolon Algılama

Otomatik olarak algılanan kolon başlıkları:

| Öğrenci No | Ad | Soyad | E-posta | Sınıf |
|-----------|----|-------|--------|-------|
| Öğrenci No | Ad | Soyad | E-posta | Sınıf |
| Ogrenci No | Adı | Soyadı | Email | Yıl |
| No | Isim | Soyisim | Mail | Class |

### Örnek Kullanım

```python
from src.views.import_view import ImportView

import_view = ImportView(parent_frame)
import_view.pack(fill='both', expand=True)
```

---

## 6. Olası Hatalar ve Çözümler

### 5.1 Controller Hataları

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| `'success': False` | Service validasyon hatası | `result['message']` kontrol et |
| `KeyError` | `data.get()` eksik parametre | Varsayılan değer kullan |
| `ValueError` | Tür dönüşümü hatası | Try-except ekle |
| `AttributeError` | Service metodu yok | Service import kontrolü |

### 5.2 View Hataları

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| `TclError` | Widget destroy edildiyse erişim | Widget varlığını kontrol et |
| `IndexError` | Seçili satır yok | `get_selected()` kontrol et |
| `ImportError` | Dinamik import hatası | Mutlak import kullan |

### 5.3 Component Hataları

| Hata | Sebebi | Çözüm |
|------|--------|-------|
| `TypeError` | Yanlış columns formatı | `[(id, label, width), ...]` kullan |
| `ValueError` | Spinbox min-max hatası | `from_` ve `to` kontrol et |
| `AttributeError` | Widget tipi yanlış | `type` parametresi kontrol et |

---

## 6. Tkinter Kullanımı

### 6.1 Layout Yönetimi

- **pack():** Basit yerleşim için
- **grid():** Tablo yerleşimi için
- **place():** Mutlak konumlandırma için

### 6.2 Event Binding

| Event | Açıklama |
|-------|----------|
| `<Button-1>` | Sol tıklama |
| `<Double-1>` | Çift tıklama |
| `<Return>` | Enter tuşu |
| `<Escape>` | ESC tuşu |
| `<FocusIn>` | Odak alma |
| `<FocusOut>` | Odak kaybetme |
| `<Enter>` | Mouse üzerine gelme |
| `<Leave>` | Mouse üzerinden ayrılma |

### 6.3 Stillendirme

```python
# ttk Style
style = ttk.Style()
style.configure('Custom.TButton', 
                font=('Segoe UI', 11),
                background='#3498db')

# Tkinter Widget
btn = tk.Button(parent, 
                text='Buton',
                bg='#3498db',
                fg='white',
                font=('Segoe UI', 11))
```

---

## 7. Performans İpuçları

1. **Lazy Loading:** View import'larını ihtiyaç anında yap
2. **Data Pagination:** Büyük veri setlerinde sayfalama kullan
3. **Debouncing:** Arama inputunda debouncing kullan
4. **Virtualization:** DataTable'ta sanal kaydırma
5. **Async Operations:** Uzun süren işlemler için threading

---

## 8. Öneriler

1. **MVVM Pattern:** Model-View-ViewModel yapısına geçiş
2. **State Management:** Global state yönetimi ekleyin
3. **Form Validation:** Daha kapsamlı validasyon
4. **Error Handling:** Merkezi hata yönetimi
5. **Testing:** UI testleri ekleyin
6. **Theming:** Dinamik tema desteği
7. **Internationalization:** Çoklu dil desteği
8. **Accessibility:** Erişilebilirlik özellikleri
9. **Responsive Layout:** Dinamik pencere boyutlandırma
10. **Progress Feedback:** Uzun işlemlerde ilerleme göstergesi
