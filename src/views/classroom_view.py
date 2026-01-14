"""
Classroom View - Derslik Yönetimi Görünümü
Derslik CRUD işlemlerini yönetir
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.views.base_crud_view import BaseCrudView


class ClassroomView(BaseCrudView):    
    title = "🚪 Derslik Yönetimi"
    columns = [
        ('id', 'ID', 50),
        ('name', 'Derslik Adı', 150),
        ('faculty_name', 'Fakülte', 200),
        ('capacity', 'Kapasite', 80),
        ('has_computer', 'Bilgisayar', 80),
        ('is_suitable', 'Sınav Uygun', 80),
        ('nearby_classrooms', 'Yakın Sınıflar', 200),
    ]
    
    def __init__(self, parent, controller):
        self.faculties = []
        self.filter_suitable_only = tk.BooleanVar(value=False)
        super().__init__(parent, controller)

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
        
        self.import_proximity_btn = tk.Button(
            btn_frame,
            text='Yakınlık Dosyası Yükle',
            font=('Segoe UI', 10),
            bg='#16a085',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._on_import_proximity
        )
        self.import_proximity_btn.pack(side='left', padx=5)
        self._add_button_hover(self.import_proximity_btn, '#16a085', '#1abc9c')
        
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

    def _on_import_proximity(self):
        file_path = filedialog.askopenfilename(
            title='Yakınlık Dosyası Seç',
            filetypes=[
                ('CSV Dosyaları', '*.csv'),
                ('Tüm Dosyalar', '*.*')
            ]
        )
        if not file_path:
            return
        
        try:
            # TODO: implement in ClassroomController: import_classroom_proximity(filepath: str) -> dict/None
            result = self.controller.import_classroom_proximity(file_path)
        except AttributeError:
            messagebox.showerror('Hata', 'Yakınlık yükleme işlemi için controller yöntemi bulunamadı.')
            return
        except Exception as exc:
            messagebox.showerror('Hata', f'Hata oluştu: {str(exc)}')
            return
        
        if isinstance(result, dict):
            if result.get('success', True):
                messagebox.showinfo('Başarılı', result.get('message', 'Yakınlık dosyası yüklendi.'))
            else:
                messagebox.showerror('Hata', result.get('message', 'Yakınlık dosyası yüklenemedi.'))
                return
        else:
            messagebox.showinfo('Başarılı', 'Yakınlık dosyası yüklendi.')
        
        self.load_data()
    
    def _create_search_bar(self):
        search_frame = tk.Frame(self, bg='#ecf0f1')
        search_frame.pack(fill='x', padx=20, pady=10)
        
        search_label = tk.Label(
            search_frame,
            text='🔍',
            font=('Segoe UI', 12),
            bg='#ecf0f1'
        )
        search_label.pack(side='left')
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search)
        
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Segoe UI', 11),
            width=40,
            bd=1,
            relief='solid'
        )
        self.search_entry.pack(side='left', padx=10, ipady=5)
        
        clear_btn = tk.Button(
            search_frame,
            text='✖',
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            fg='#7f8c8d',
            bd=0,
            cursor='hand2',
            command=lambda: self.search_var.set('')
        )
        clear_btn.pack(side='left')
        
        filter_frame = tk.Frame(self, bg='#ecf0f1')
        filter_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        separator = ttk.Separator(filter_frame, orient='horizontal')
        separator.pack(fill='x', pady=5)
        
        filter_inner_frame = tk.Frame(filter_frame, bg='#ecf0f1')
        filter_inner_frame.pack(fill='x')
        
        filter_label = tk.Label(
            filter_inner_frame,
            text='🔍 Filtreleme:',
            font=('Segoe UI', 10, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        filter_label.pack(side='left', padx=(0, 10))
        
        self.suitable_checkbox = tk.Checkbutton(
            filter_inner_frame,
            text="Sadece Sınav Yapılabilecek Derslikleri Göster",
            variable=self.filter_suitable_only,
            command=self._on_filter_change,
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            activebackground='#ecf0f1',
            fg='#2c3e50',
            selectcolor='#ffffff'
        )
        self.suitable_checkbox.pack(side='left', padx=10)
    
    def _on_filter_change(self):
        self.load_data(self.search_var.get().lower() if hasattr(self, 'search_var') else '')
    
    def get_form_fields(self):
        self.faculties = self.controller.get_all_faculties()
        faculty_options = [(f.id, f.name) for f in self.faculties]
        
        return [
            {
                'name': 'name',
                'label': 'Derslik Adı',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'faculty_id',
                'label': 'Fakülte',
                'type': 'combo',
                'options': faculty_options,
                'required': True
            },
            {
                'name': 'capacity',
                'label': 'Kapasite (Öğrenci)',
                'type': 'spinbox',
                'min': 1,
                'max': 500,
                'default': 30,
                'required': True
            },
            {
                'name': 'has_computer',
                'label': 'Bilgisayar Var',
                'type': 'checkbox',
                'default': True
            },
            {
                'name': 'is_suitable',
                'label': 'Sınav Yapılabilir',
                'type': 'checkbox',
                'default': True
            }
        ]
    
    def load_data(self, search_term=''):
        if self.filter_suitable_only.get():
            classrooms = self.controller.get_exam_suitable_classrooms()
        else:
            classrooms = self.controller.get_all_classrooms()
        
        data = []
        for classroom in classrooms:
            nearby = getattr(classroom, 'nearby_classrooms', None)
            if nearby is None:
                nearby = getattr(classroom, 'neighbor_classrooms', None)
            if nearby is None:
                nearby = getattr(classroom, 'adjacent_classrooms', None)
            if isinstance(nearby, (list, tuple)):
                nearby_display = ', '.join(str(item) for item in nearby) if nearby else '-'
            elif isinstance(nearby, str):
                nearby_display = nearby if nearby.strip() else '-'
            else:
                nearby_display = '-'

            row = {
                'id': classroom.id,
                'name': classroom.name,
                'faculty_name': classroom.faculty_name if classroom.faculty_name else 'Belirsiz',
                'capacity': classroom.capacity,
                'has_computer': '✓' if classroom.has_computer else '✗',
                'is_suitable': '✓' if classroom.is_suitable else '✗',
                'nearby_classrooms': nearby_display
            }
            
            if search_term:
                searchable = f"{row['name']} {row['faculty_name']}".lower()
                if search_term not in searchable:
                    continue
            
            data.append(row)
        
        self.data_table.load_data(data)
    
    def validate_form(self, data):
        if not data.get('name'):
            return False, "Derslik adı zorunludur."
        if not data.get('faculty_id'):
            return False, "Fakülte seçimi zorunludur."
        
        capacity = data.get('capacity', 0)
        
        if capacity < 1:
            return False, "Kapasite en az 1 olmalıdır."
        
        return True, ""
    
    def create_item(self, data):
        return self.controller.create_classroom({
            'name': data['name'],
            'faculty_id': data['faculty_id'],
            'capacity': data['capacity'],
            'has_computer': data.get('has_computer', False),
            'is_suitable': data.get('is_suitable', True)
        })
    
    def update_item(self, id, data):
        return self.controller.update_classroom(id, {
            'name': data['name'],
            'faculty_id': data['faculty_id'],
            'capacity': data['capacity'],
            'has_computer': data.get('has_computer', False),
            'is_suitable': data.get('is_suitable', True)
        })
    
    def delete_item(self, id):
        return self.controller.delete_classroom(id)
    
    def get_edit_data(self, item_id):
        classrooms = self.controller.get_all_classrooms()
        for classroom in classrooms:
            if classroom.id == item_id:
                return {
                    'name': classroom.name,
                    'faculty_id': classroom.faculty_id,
                    'capacity': classroom.capacity,
                    'has_computer': classroom.has_computer,
                    'is_suitable': classroom.is_suitable
                }
        return None
