"""
Lecturer View - Öğretim Üyesi Yönetimi Görünümü
- Admin: Tüm öğretim üyelerini yönetir
- Bölüm Yetkilisi: Sadece kendi bölümündeki öğretim üyelerini yönetir
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.views.base_crud_view import BaseCrudView
from src.models.lecturer import ALL_WEEKDAYS


class LecturerView(BaseCrudView):
    
    title = "👨‍🏫 Öğretim Üyesi Yönetimi"
    columns = [
        ('id', 'ID', 50),
        ('title', 'Unvan', 80),
        ('name', 'Ad Soyad', 200),
        ('department_name', 'Bölüm', 200),
        ('email', 'E-posta', 200),
        ('available_days', 'Müsait Günler', 150),
    ]
    
    def __init__(self, parent, dashboard):
        self.user_role = dashboard.get_user_role()
        self.user_department_id = dashboard.get_user_department_id()
        
        super().__init__(parent, dashboard)
    
    def get_form_fields(self):
        departments = self.controller.get_all_departments()
        
        if self.user_role == 'bolum_yetkilisi' and self.user_department_id:
            department_options = [(d.id, d.name) for d in departments if d.is_active and d.id == self.user_department_id]
        else:
            department_options = [(d.id, d.name) for d in departments if d.is_active]
        
        title_options = [
            'Prof. Dr.',
            'Doç. Dr.',
            'Dr. Öğr. Üyesi',
            'Öğr. Gör. Dr.',
            'Öğr. Gör.',
            'Arş. Gör. Dr.',
            'Arş. Gör.'
        ]
        
        return [
            {
                'name': 'department_id',
                'label': 'Bölüm',
                'type': 'combo',
                'options': department_options,
                'required': True
            },
            {
                'name': 'title',
                'label': 'Unvan',
                'type': 'combo',
                'options': title_options,
                'editable': True,
                'required': False
            },
            {
                'name': 'first_name',
                'label': 'Ad',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'last_name',
                'label': 'Soyad',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'email',
                'label': 'E-posta (Otomatik oluşturulur)',
                'type': 'entry',
                'required': False
            },
            {
                'name': 'available_days',
                'label': 'Müsait Günler',
                'type': 'multi_checkbox',
                'options': ALL_WEEKDAYS,
                'default': ALL_WEEKDAYS.copy()
            }
        ]
    
    def load_data(self, search_term=''):
        lecturers = self.controller.get_all_lecturers()
        departments = {d.id: d.name for d in self.controller.get_all_departments()}
        
        if self.user_role == 'bolum_yetkilisi' and self.user_department_id:
            lecturers = [l for l in lecturers if l.department_id == self.user_department_id]
        
        data = []
        for lecturer in lecturers:
            full_name = f"{lecturer.first_name} {lecturer.last_name}"
            
            available_days_display = lecturer.available_days_display
            
            row = {
                'id': lecturer.id,
                'title': lecturer.title or '-',
                'name': full_name,
                'first_name': lecturer.first_name,
                'last_name': lecturer.last_name,
                'department_id': lecturer.department_id,
                'department_name': departments.get(lecturer.department_id, '-'),
                'email': lecturer.email or '-',
                'available_days': available_days_display,
                'available_days_list': lecturer.available_days  # Form düzenleme için
            }
            
            if search_term:
                searchable = f"{lecturer.title} {row['name']} {row['department_name']} {row['email']}".lower()
                if search_term not in searchable:
                    continue
            
            data.append(row)
        
        self.data_table.load_data(data)
    
    def validate_form(self, data):
        if not data.get('department_id'):
            return False, "Bölüm seçimi zorunludur."
        if not data.get('first_name'):
            return False, "Ad zorunludur."
        if not data.get('last_name'):
            return False, "Soyad zorunludur."
        
        if self.user_role == 'bolum_yetkilisi' and self.user_department_id:
            if data.get('department_id') != self.user_department_id:
                return False, "Sadece kendi bölümünüze öğretim üyesi ekleyebilirsiniz."
        
        email = data.get('email', '')
        if email and '@' not in email:
            return False, "Geçerli bir e-posta adresi girin."
        
        available_days = data.get('available_days', [])
        if not available_days:
            return False, "En az bir müsait gün seçmelisiniz."
        
        return True, ""
    
    def create_item(self, data):
        return self.controller.create_lecturer({
            'department_id': data['department_id'],
            'title': data.get('title', ''),
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data.get('email', ''),
            'available_days': data.get('available_days', ALL_WEEKDAYS.copy())
        })
    
    def update_item(self, id, data):
        return self.controller.update_lecturer(id, {
            'department_id': data['department_id'],
            'title': data.get('title', ''),
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'email': data.get('email', ''),
            'available_days': data.get('available_days', ALL_WEEKDAYS.copy())
        })
    
    def delete_item(self, id):
        return self.controller.delete_lecturer(id)
    
    def get_edit_data(self, row_data):
        available_days = row_data.get('available_days_list', ALL_WEEKDAYS.copy())
        
        return {
            'department_id': row_data.get('department_id'),
            'title': row_data.get('title', ''),
            'first_name': row_data.get('first_name', ''),
            'last_name': row_data.get('last_name', ''),
            'email': row_data.get('email', ''),
            'available_days': available_days
        }
