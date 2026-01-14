"""
Course View - Ders Yönetimi Görünümü
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from src.views.base_crud_view import BaseCrudView
from src.models.course import COURSE_TYPES, COURSE_TYPE_MAP, EXAM_TYPES, EXAM_DURATION_OPTIONS


class CourseView(BaseCrudView):    
    title = "📖 Ders Yönetimi"
    columns = [
        ('id', 'ID', 50),
        ('code', 'Ders Kodu', 100),
        ('name', 'Ders Adı', 180),
        ('department_name', 'Bölüm', 130),
        ('lecturer_name', 'Öğretim Üyesi', 130),
        ('credit', 'Kredi', 50),
        ('student_count', 'Öğrenci', 60),
        ('registered_student_count', 'Kayıtlı Öğrenci Sayısı', 140),
        ('lecturer_count', 'Ö.Üye', 50),
        ('semester', 'Dönem', 60),
        ('type', 'Tür', 90),
        ('exam_type', 'Sınav Türü', 80),
        ('exam_duration', 'Süre', 60),
    ]
    
    def __init__(self, parent, dashboard):
        self.user_role = dashboard.get_user_role()
        self.user_department_id = dashboard.get_user_department_id()
        
        super().__init__(parent, dashboard)

    def _create_header(self):
        header_frame = tk.Frame(self, bg='#ecf0f1')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            header_frame,
            text=self.title,
            font=('Segoe UI', 20, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        title_label.pack(side='left')
        
        btn_frame = tk.Frame(header_frame, bg='#ecf0f1')
        btn_frame.pack(side='right')
        
        self.add_btn = tk.Button(
            btn_frame,
            text='➕ Ekle',
            font=('Segoe UI', 10),
            bg='#27ae60',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._on_add
        )
        self.add_btn.pack(side='left', padx=5)
        self._add_button_hover(self.add_btn, '#27ae60', '#2ecc71')
        
        self.edit_btn = tk.Button(
            btn_frame,
            text='✏️ Düzenle',
            font=('Segoe UI', 10),
            bg='#3498db',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._on_edit
        )
        self.edit_btn.pack(side='left', padx=5)
        self._add_button_hover(self.edit_btn, '#3498db', '#5dade2')
        
        self.delete_btn = tk.Button(
            btn_frame,
            text='🗑️ Sil',
            font=('Segoe UI', 10),
            bg='#e74c3c',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._on_delete
        )
        self.delete_btn.pack(side='left', padx=5)
        self._add_button_hover(self.delete_btn, '#e74c3c', '#ec7063')
        
        self.upload_list_btn = tk.Button(
            btn_frame,
            text='Sınıf Listesi Yükle',
            font=('Segoe UI', 10),
            bg='#16a085',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._on_upload_class_list
        )
        self.upload_list_btn.pack(side='left', padx=5)
        self._add_button_hover(self.upload_list_btn, '#16a085', '#1abc9c')
        
        self.refresh_btn = tk.Button(
            btn_frame,
            text='🔄 Yenile',
            font=('Segoe UI', 10),
            bg='#95a5a6',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.load_data
        )
        self.refresh_btn.pack(side='left', padx=5)
        self._add_button_hover(self.refresh_btn, '#95a5a6', '#bdc3c7')

    def _on_upload_class_list(self):
        selected = self.data_table.get_selected()
        if not selected:
            messagebox.showwarning('Uyarı', 'Lütfen sınıf listesi yüklemek için bir ders seçin.')
            return
        
        course_code = selected.get('code') or selected.get('course_code')
        if not course_code:
            messagebox.showwarning('Uyarı', 'Seçilen ders için ders kodu bulunamadı.')
            return
        
        file_path = filedialog.askopenfilename(
            title='Sınıf Listesi Seç',
            filetypes=[
                ('CSV Dosyaları', '*.csv'),
                ('Excel Dosyaları', '*.xlsx *.xls'),
                ('Tüm Dosyalar', '*.*')
            ]
        )
        if not file_path:
            return
        
        try:
            # TODO: implement in CourseController: import_class_list(course_code: str, filepath: str) -> dict/None
            result = self.controller.import_class_list(course_code, file_path)
        except AttributeError:
            messagebox.showerror('Hata', 'Sınıf listesi yükleme işlemi için controller yöntemi bulunamadı.')
            return
        except Exception as exc:
            messagebox.showerror('Hata', f'Hata oluştu: {str(exc)}')
            return
        
        if isinstance(result, dict):
            if result.get('success', True):
                messagebox.showinfo('Başarılı', result.get('message', 'Sınıf listesi yüklendi.'))
            else:
                messagebox.showerror('Hata', result.get('message', 'Sınıf listesi yüklenemedi.'))
                return
        else:
            messagebox.showinfo('Başarılı', 'Sınıf listesi yüklendi.')
        
        self.load_data()
    
    def get_form_fields(self):
        departments = self.controller.get_all_departments()
        
        if self.user_role == 'bolum_yetkilisi' and self.user_department_id:
            department_options = [(d.id, d.name) for d in departments if d.is_active and d.id == self.user_department_id]
        else:
            department_options = [(d.id, d.name) for d in departments if d.is_active]
        
        lecturers = self.controller.get_all_lecturers()
        
        if self.user_role == 'bolum_yetkilisi' and self.user_department_id:
            lecturers = [l for l in lecturers if l.department_id == self.user_department_id]
        
        lecturer_options = [(l.id, f"{l.title or ''} {l.first_name} {l.last_name}".strip())
                            for l in lecturers]
        
        return [
            {
                'name': 'department_id',
                'label': 'Bölüm',
                'type': 'combo',
                'options': department_options,
                'required': True
            },
            {
                'name': 'lecturer_id',
                'label': 'Öğretim Üyesi',
                'type': 'combo',
                'options': lecturer_options,
                'required': True
            },
            {
                'name': 'code',
                'label': 'Ders Kodu',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'name',
                'label': 'Ders Adı',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'credit',
                'label': 'Kredi',
                'type': 'spinbox',
                'min': 1,
                'max': 10,
                'default': 3,
                'required': True
            },
            {
                'name': 'student_count',
                'label': 'Öğrenci Sayısı',
                'type': 'spinbox',
                'min': 0,
                'max': 500,
                'default': 30,
                'required': True
            },
            {
                'name': 'lecturer_count',
                'label': 'Öğretim Üyesi Sayısı',
                'type': 'spinbox',
                'min': 1,
                'max': 10,
                'default': 1,
                'required': True
            },
            {
                'name': 'theory_hours',
                'label': 'Teori Saati',
                'type': 'spinbox',
                'min': 0,
                'max': 20,
                'default': 3,
                'required': False
            },
            {
                'name': 'lab_hours',
                'label': 'Laboratuvar Saati',
                'type': 'spinbox',
                'min': 0,
                'max': 20,
                'default': 0,
                'required': False
            },
            {
                'name': 'semester',
                'label': 'Dönem',
                'type': 'spinbox',
                'min': 1,
                'max': 8,
                'default': 1,
                'required': True
            },
            {
                'name': 'type',
                'label': 'Ders Türü',
                'type': 'combo',
                'options': COURSE_TYPES,
                'required': True
            },
            {
                'name': 'has_exam',
                'label': 'Sınav Var mı?',
                'type': 'checkbox',
                'default': True
            },
            {
                'name': 'exam_type',
                'label': 'Sınav Türü',
                'type': 'combo',
                'options': EXAM_TYPES,
                'required': False
            },
            {
                'name': 'exam_duration',
                'label': 'Sınav Süresi',
                'type': 'combo',
                'options': EXAM_DURATION_OPTIONS,
                'required': False
            },
            {
                'name': 'description',
                'label': 'Açıklama',
                'type': 'text',
                'required': False
            }
        ]
    
    def load_data(self, search_term=''):
        courses = self.controller.get_all_courses()
        departments = {d.id: d.name for d in self.controller.get_all_departments()}
        lecturers = {l.id: f"{l.title or ''} {l.first_name} {l.last_name}".strip()
                    for l in self.controller.get_all_lecturers()}
        
        if self.user_role == 'bolum_yetkilisi' and self.user_department_id:
            courses = [c for c in courses if c.department_id == self.user_department_id]
        
        data = []
        for course in courses:
            type_display = COURSE_TYPE_MAP.get(course.course_type, course.course_type)
            
            if course.has_exam and course.exam_duration > 0:
                exam_duration_display = f"{course.exam_duration} dk"
            else:
                exam_duration_display = "-"
            
            if course.has_exam and course.exam_type:
                exam_type_display = course.exam_type
            else:
                exam_type_display = "-"

            registered_count = getattr(course, 'registered_student_count', None)
            if registered_count is None:
                registered_count = getattr(course, 'enrolled_student_count', None)
            if registered_count is None:
                registered_count = getattr(course, 'registered_students', None)
            registered_count_display = registered_count if registered_count is not None else '-'
            
            row = {
                'id': course.id,
                'code': course.code,
                'name': course.name,
                'department_id': course.department_id,
                'department_name': departments.get(course.department_id, '-'),
                'lecturer_id': course.lecturer_id,
                'lecturer_name': lecturers.get(course.lecturer_id, '-'),
                'credit': course.credit if course.credit else 3,
                'student_count': course.student_count if course.student_count else 0,
                'registered_student_count': registered_count_display,
                'lecturer_count': course.lecturer_count if course.lecturer_count else 1,
                'semester': f"{course.period}. Dönem" if course.period else '-',
                '_semester_value': course.period if course.period else 1,
                '_credit_value': course.credit if course.credit else 3,
                '_student_count_value': course.student_count if course.student_count else 0,
                '_lecturer_count_value': course.lecturer_count if course.lecturer_count else 1,
                '_theory_hours': course.theory_hours if course.theory_hours else 0,
                '_lab_hours': course.lab_hours if course.lab_hours else 0,
                'type': type_display,
                '_type_value': course.course_type,
                'exam_type': exam_type_display,
                '_exam_type_value': course.exam_type if course.exam_type else 'Yazılı',
                'exam_duration': exam_duration_display,
                '_exam_duration_value': course.exam_duration if course.exam_duration else 60,
                'has_exam': 'Evet' if course.has_exam else 'Hayır',
                '_has_exam_value': course.has_exam,
                'description': course.description or ''
            }
            
            if search_term:
                searchable = f"{row['code']} {row['name']} {row['department_name']} {row['lecturer_name']} {row['type']} {row['exam_type']}".lower()
                if search_term not in searchable:
                    continue
            
            data.append(row)
        
        self.data_table.load_data(data)
    
    def validate_form(self, data):
        if not data.get('department_id'):
            return False, "Bölüm seçimi zorunludur."
        if not data.get('lecturer_id'):
            return False, "Öğretim üyesi seçimi zorunludur."
        if not data.get('code'):
            return False, "Ders kodu zorunludur."
        if not data.get('name'):
            return False, "Ders adı zorunludur."
        
        if self.user_role == 'bolum_yetkilisi' and self.user_department_id:
            if data.get('department_id') != self.user_department_id:
                return False, "Sadece kendi bölümünüze ders ekleyebilirsiniz."
        
        if len(data['code']) > 15:
            return False, "Ders kodu en fazla 15 karakter olabilir."
        
        credit = data.get('credit', 0)
        if credit < 1:
            return False, "Kredi en az 1 olmalıdır."
        
        student_count = data.get('student_count', 0)
        if student_count < 0:
            return False, "Öğrenci sayısı negatif olamaz."
        
        lecturer_count = data.get('lecturer_count', 1)
        if lecturer_count < 1:
            return False, "Öğretim üyesi sayısı en az 1 olmalıdır."
        
        has_exam = data.get('has_exam', True)
        if has_exam:
            exam_duration = data.get('exam_duration', 60)
            if exam_duration not in [30, 60, 90, 120]:
                return False, "Sınav süresi 30, 60, 90 veya 120 dakika olmalıdır."
        
        return True, ""
    
    def create_item(self, data):
        has_exam = data.get('has_exam', True)
        if data.get('type') == 'Proje':
            has_exam = False
        
        exam_type = data.get('exam_type', 'Yazılı') if has_exam else ""
        exam_duration = data.get('exam_duration', 60) if has_exam else 0
        
        return self.controller.create_course({
            'department_id': data['department_id'],
            'lecturer_id': data['lecturer_id'],
            'code': data['code'],
            'name': data['name'],
            'credit': data['credit'],
            'student_count': data.get('student_count', 0),
            'lecturer_count': data.get('lecturer_count', 1),
            'theory_hours': data.get('theory_hours', 0),
            'lab_hours': data.get('lab_hours', 0),
            'period': data.get('semester', 1),
            'course_type': data['type'],
            'has_exam': has_exam,
            'exam_type': exam_type,
            'exam_duration': exam_duration,
            'description': data.get('description', '')
        })
    
    def update_item(self, id, data):
        has_exam = data.get('has_exam', True)
        if data.get('type') == 'Proje':
            has_exam = False
        
        exam_type = data.get('exam_type', 'Yazılı') if has_exam else ""
        exam_duration = data.get('exam_duration', 60) if has_exam else 0
        
        return self.controller.update_course(id, {
            'department_id': data['department_id'],
            'lecturer_id': data['lecturer_id'],
            'code': data['code'],
            'name': data['name'],
            'credit': data['credit'],
            'student_count': data.get('student_count', 0),
            'lecturer_count': data.get('lecturer_count', 1),
            'theory_hours': data.get('theory_hours', 0),
            'lab_hours': data.get('lab_hours', 0),
            'period': data.get('semester', 1),
            'course_type': data['type'],
            'has_exam': has_exam,
            'exam_type': exam_type,
            'exam_duration': exam_duration,
            'description': data.get('description', '')
        })
    
    def delete_item(self, id):
        return self.controller.delete_course(id)
