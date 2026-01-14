"""
Faculty View - Fakülte Yönetimi Görünümü
"""

import tkinter as tk
from tkinter import messagebox
from src.views.base_crud_view import BaseCrudView


class FacultyView(BaseCrudView):    
    title = "🏛️ Fakülte Yönetimi"
    columns = [
        ('id', 'ID', 50),
        ('code', 'Kod', 100),
        ('name', 'Fakülte Adı', 300),
        ('dean_name', 'Dekan', 200),
        ('is_active', 'Durum', 80),
    ]
    
    def get_form_fields(self):
        return [
            {
                'name': 'code',
                'label': 'Fakülte Kodu',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'name',
                'label': 'Fakülte Adı',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'dean_name',
                'label': 'Dekan Adı',
                'type': 'entry',
                'required': False
            },
            {
                'name': 'is_active',
                'label': 'Aktif',
                'type': 'checkbox',
                'default': True
            }
        ]
    
    def load_data(self, search_term=''):
        faculties = self.controller.get_all_faculties()
        
        data = []
        for faculty in faculties:
            row = {
                'id': faculty.id,
                'code': faculty.code,
                'name': faculty.name,
                'dean_name': faculty.dean_name or '-',
                'is_active': 'Aktif' if faculty.is_active else 'Pasif'
            }
            
            if search_term:
                searchable = f"{row['code']} {row['name']} {row['dean_name']}".lower()
                if search_term not in searchable:
                    continue
            
            data.append(row)
        
        self.data_table.load_data(data)
    
    def validate_form(self, data):
        if not data.get('code'):
            return False, "Fakülte kodu zorunludur."
        if not data.get('name'):
            return False, "Fakülte adı zorunludur."
        if len(data['code']) > 10:
            return False, "Fakülte kodu en fazla 10 karakter olabilir."
        return True, ""
    
    def create_item(self, data):
        return self.controller.create_faculty({
            'code': data['code'],
            'name': data['name'],
            'dean_name': data.get('dean_name', ''),
            'is_active': data.get('is_active', True)
        })
    
    def update_item(self, id, data):
        return self.controller.update_faculty(id, {
            'code': data['code'],
            'name': data['name'],
            'dean_name': data.get('dean_name', ''),
            'is_active': data.get('is_active', True)
        })
    
    def delete_item(self, id):
        departments = self.controller.get_departments_by_faculty(id)
        if departments:
            messagebox.showwarning(
                'Silme Engellendi',
                f'Bu fakülteye bağlı {len(departments)} bölüm var. Önce bölümleri silin veya taşıyın.'
            )
            return {'success': False, 'message': 'Bağlı bölümler var.'}
        
        return self.controller.delete_faculty(id)
