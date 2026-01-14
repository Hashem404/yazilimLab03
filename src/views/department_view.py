"""
Department View - Bölüm Yönetimi Görünümü
"""

import tkinter as tk
from tkinter import messagebox
from src.views.base_crud_view import BaseCrudView


class DepartmentView(BaseCrudView):    
    title = "📚 Bölüm Yönetimi"
    columns = [
        ('id', 'ID', 50),
        ('code', 'Kod', 100),
        ('name', 'Bölüm Adı', 250),
        ('faculty_name', 'Fakülte', 200),
        ('head_of_department', 'Bölüm Başkanı', 150),
        ('is_active', 'Durum', 80),
    ]
    
    def get_form_fields(self):
        faculties = self.controller.get_all_faculties()
        faculty_options = [(f.id, f.name) for f in faculties if f.is_active]
        
        return [
            {
                'name': 'faculty_id',
                'label': 'Fakülte',
                'type': 'combo',
                'options': faculty_options,
                'required': True
            },
            {
                'name': 'code',
                'label': 'Bölüm Kodu',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'name',
                'label': 'Bölüm Adı',
                'type': 'entry',
                'required': True
            },
            {
                'name': 'head_of_department',
                'label': 'Bölüm Başkanı',
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
        departments = self.controller.get_all_departments()
        faculties = {f.id: f.name for f in self.controller.get_all_faculties()}
        
        data = []
        for dept in departments:
            row = {
                'id': dept.id,
                'code': dept.code,
                'name': dept.name,
                'faculty_id': dept.faculty_id,
                'faculty_name': faculties.get(dept.faculty_id, '-'),
                'head_of_department': dept.head_of_department or '-',
                'is_active': 'Aktif' if dept.is_active else 'Pasif'
            }
            
            if search_term:
                searchable = f"{row['code']} {row['name']} {row['faculty_name']} {row['head_of_department']}".lower()
                if search_term not in searchable:
                    continue
            
            data.append(row)
        
        self.data_table.load_data(data)
    
    def validate_form(self, data):
        if not data.get('faculty_id'):
            return False, "Fakülte seçimi zorunludur."
        if not data.get('code'):
            return False, "Bölüm kodu zorunludur."
        if not data.get('name'):
            return False, "Bölüm adı zorunludur."
        if len(data['code']) > 10:
            return False, "Bölüm kodu en fazla 10 karakter olabilir."
        return True, ""
    
    def create_item(self, data):
        return self.controller.create_department({
            'faculty_id': data['faculty_id'],
            'code': data['code'],
            'name': data['name'],
            'head_of_department': data.get('head_of_department', ''),
            'is_active': data.get('is_active', True)
        })
    
    def update_item(self, id, data):
        return self.controller.update_department(id, {
            'faculty_id': data['faculty_id'],
            'code': data['code'],
            'name': data['name'],
            'head_of_department': data.get('head_of_department', ''),
            'is_active': data.get('is_active', True)
        })
    
    def delete_item(self, id):
        lecturers = self.controller.get_lecturers_by_department(id)
        if lecturers:
            messagebox.showwarning(
                'Silme Engellendi',
                f'Bu bölüme bağlı {len(lecturers)} öğretim üyesi var. Önce öğretim üyelerini silin veya taşıyın.'
            )
            return {'success': False, 'message': 'Bağlı öğretim üyeleri var.'}
        
        return self.controller.delete_department(id)
