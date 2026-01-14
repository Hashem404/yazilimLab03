"""
Reports View - Raporlama Ekranı Görünümü
Excel rapor oluşturma işlemlerini yönetir
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime, timedelta


class ReportsView(tk.Frame):
    """Raporlama ekranı"""
    
    def __init__(self, parent, dashboard):
        super().__init__(parent, bg='#ecf0f1')
        self.dashboard = dashboard
        self.controller = dashboard.controller
        
        self._create_widgets()
    
    def _create_widgets(self):
        title_frame = tk.Frame(self, bg='#ecf0f1')
        title_frame.pack(fill='x', padx=30, pady=(30, 20))
        
        title = tk.Label(
            title_frame,
            text='📊 Raporlar',
            font=('Segoe UI', 24, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        title.pack(anchor='w')
        
        subtitle = tk.Label(
            title_frame,
            text='Sınav programı raporlarını oluşturun ve dışa aktarın',
            font=('Segoe UI', 11),
            bg='#ecf0f1',
            fg='#7f8c8d'
        )
        subtitle.pack(anchor='w')
        
        cards_frame = tk.Frame(self, bg='#ecf0f1')
        cards_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        self._create_report_card(
            cards_frame,
            '📅 Sınav Programı Raporu',
            'Belirli tarih aralığındaki sınav programını Excel formatında dışa aktarın.',
            '#3498db',
            self._show_exam_schedule_report
        )
        
        self._create_report_card(
            cards_frame,
            '🏢 Fakülte/Bölüm Bazlı Rapor',
            'Fakülte veya bölüm bazında sınav programlarını görüntüleyin ve dışa aktarın.',
            '#9b59b6',
            self._show_faculty_report
        )
    
    def _create_report_card(self, parent, title, description, color, command):
        card = tk.Frame(parent, bg='white', bd=1, relief='solid')
        card.pack(fill='x', pady=8)

        color_bar = tk.Frame(card, bg=color, width=5)
        color_bar.pack(side='left', fill='y')

        content = tk.Frame(card, bg='white', padx=20, pady=15)
        content.pack(side='left', fill='both', expand=True)
        
        title_label = tk.Label(
            content,
            text=title,
            font=('Segoe UI', 13, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(anchor='w')
        
        desc_label = tk.Label(
            content,
            text=description,
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            wraplength=500,
            justify='left'
        )
        desc_label.pack(anchor='w', pady=(5, 0))

        btn_frame = tk.Frame(card, bg='white', padx=15)
        btn_frame.pack(side='right', fill='y')
        
        btn = tk.Button(
            btn_frame,
            text='Oluştur →',
            font=('Segoe UI', 10),
            bg=color,
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=command
        )
        btn.pack(expand=True)

        def on_enter(e):
            card.config(bg='#f8f9fa')
            content.config(bg='#f8f9fa')
            title_label.config(bg='#f8f9fa')
            desc_label.config(bg='#f8f9fa')
            btn_frame.config(bg='#f8f9fa')
        
        def on_leave(e):
            card.config(bg='white')
            content.config(bg='white')
            title_label.config(bg='white')
            desc_label.config(bg='white')
            btn_frame.config(bg='white')
        
        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
    
    def _show_exam_schedule_report(self):
        dialog = ExamScheduleReportDialog(self, self.controller)
        dialog.grab_set()
    
    def _show_faculty_report(self):
        dialog = FacultyReportDialog(self, self.controller)
        dialog.grab_set()


class BaseReportDialog(tk.Toplevel):
    
    def __init__(self, parent, controller, title, width=500, height=400):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        
        self.title(title)
        self.geometry(f'{width}x{height}')
        self.resizable(False, False)
        self.configure(bg='#ecf0f1')
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f'+{x}+{y}')
        
        self._create_widgets()
    
    def _create_widgets(self):
        pass
    
    def _export_excel(self, data, filename_prefix):
        try:
            from src.controllers.export_controller import ExportController
            
            filepath = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[('Excel dosyaları', '*.xlsx')],
                initialfile=f'{filename_prefix}_{date.today()}.xlsx'
            )
            
            if filepath:
                export_ctrl = ExportController()
                result = export_ctrl.export_to_excel(data=data, file_path=filepath)
                if result.get('success'):
                    messagebox.showinfo('Başarılı', f'Rapor kaydedildi:\n{filepath}')
                else:
                    messagebox.showerror('Hata', result.get('message', 'Dışa aktarma başarısız'))
        except ImportError:
            messagebox.showerror('Hata', 'Excel dışa aktarma modülü bulunamadı.')
        except Exception as e:
            messagebox.showerror('Hata', f'Dışa aktarma hatası: {str(e)}')


class ExamScheduleReportDialog(BaseReportDialog):
    
    def __init__(self, parent, controller):
        super().__init__(parent, controller, '📅 Sınav Programı Raporu', 500, 300)
    
    def _create_widgets(self):
        tk.Label(
            self,
            text='Sınav Programı Raporu',
            font=('Segoe UI', 14, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=(20, 15))
        
        form = tk.Frame(self, bg='#ecf0f1')
        form.pack(fill='x', padx=30)
        
        tk.Label(form, text='Başlangıç Tarihi:', font=('Segoe UI', 10), bg='#ecf0f1').pack(anchor='w')
        self.start_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        tk.Entry(form, textvariable=self.start_var, font=('Segoe UI', 11)).pack(fill='x', pady=(0, 10), ipady=5)

        tk.Label(form, text='Bitiş Tarihi:', font=('Segoe UI', 10), bg='#ecf0f1').pack(anchor='w')
        end_date = date.today() + timedelta(days=30)
        self.end_var = tk.StringVar(value=end_date.strftime('%Y-%m-%d'))
        tk.Entry(form, textvariable=self.end_var, font=('Segoe UI', 11)).pack(fill='x', pady=(0, 20), ipady=5)

        btn_frame = tk.Frame(self, bg='#ecf0f1')
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame, text='📥 Excel Olarak İndir', font=('Segoe UI', 11), bg='#3498db', fg='white',
            bd=0, padx=20, pady=10, cursor='hand2', command=self._generate
        ).pack(side='left', padx=5)
        
        tk.Button(
            btn_frame, text='❌ Kapat', font=('Segoe UI', 11), bg='#95a5a6', fg='white',
            bd=0, padx=20, pady=10, cursor='hand2', command=self.destroy
        ).pack(side='left', padx=5)
    
    def _generate(self):
        try:
            start = datetime.strptime(self.start_var.get(), '%Y-%m-%d').date()
            end = datetime.strptime(self.end_var.get(), '%Y-%m-%d').date()
        except ValueError:
            messagebox.showerror('Hata', 'Geçersiz tarih formatı (YYYY-MM-DD)')
            return
        
        exams = self.controller.get_upcoming_exams(days=(end - start).days + 30)
        
        filtered = [e for e in exams if start <= datetime.strptime(str(e['date']), '%Y-%m-%d').date() <= end]
        
        if not filtered:
            messagebox.showinfo('Bilgi', 'Bu tarih aralığında sınav bulunamadı.')
            return
        
        self._export_excel(filtered, 'sinav_programi')


class FacultyReportDialog(BaseReportDialog):
    
    def __init__(self, parent, controller):
        super().__init__(parent, controller, '🏢 Fakülte/Bölüm Sınav Programı Raporu', 500, 370)
    
    def _create_widgets(self):
        tk.Label(
            self, text='Fakülte/Bölüm Bazlı Sınav Raporu', font=('Segoe UI', 14, 'bold'),
            bg='#ecf0f1', fg='#2c3e50'
        ).pack(pady=(20, 10))
        
        tk.Label(
            self, text='Seçilen fakülte veya bölüme ait sınav programlarını görüntüleyin ve dışa aktarın.',
            font=('Segoe UI', 9), bg='#ecf0f1', fg='#7f8c8d', wraplength=400
        ).pack(pady=(0, 15))
        
        form = tk.Frame(self, bg='#ecf0f1')
        form.pack(fill='x', padx=30)
    
        tk.Label(form, text='Fakülte:', font=('Segoe UI', 10), bg='#ecf0f1').pack(anchor='w')
        faculties = self.controller.get_all_faculties()
        faculty_names = ['Tümü'] + [f.name for f in faculties]
        self.faculty_var = tk.StringVar(value='Tümü')
        faculty_combo = ttk.Combobox(form, textvariable=self.faculty_var, values=faculty_names, state='readonly')
        faculty_combo.pack(fill='x', pady=(0, 10), ipady=3)
        self.faculties = faculties
        self.departments = [] 
        
        tk.Label(form, text='Bölüm:', font=('Segoe UI', 10), bg='#ecf0f1').pack(anchor='w')
        self.dept_var = tk.StringVar(value='Tümü')
        self.dept_combo = ttk.Combobox(form, textvariable=self.dept_var, values=['Tümü'], state='readonly')
        self.dept_combo.pack(fill='x', pady=(0, 20), ipady=3)
        
        faculty_combo.bind('<<ComboboxSelected>>', self._on_faculty_change)
        
        btn_frame = tk.Frame(self, bg='#ecf0f1')
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text='📥 Excel Olarak İndir', font=('Segoe UI', 11), bg='#9b59b6', fg='white',
                  bd=0, padx=20, pady=10, cursor='hand2', command=self._generate).pack(side='left', padx=5)
        tk.Button(btn_frame, text='❌ Kapat', font=('Segoe UI', 11), bg='#95a5a6', fg='white',
                  bd=0, padx=20, pady=10, cursor='hand2', command=self.destroy).pack(side='left', padx=5)
    
    def _on_faculty_change(self, event):
        """Fakülte değiştiğinde bölümleri güncelle"""
        faculty_name = self.faculty_var.get()
        if faculty_name == 'Tümü':
            self.dept_combo['values'] = ['Tümü']
            self.departments = []
        else:
            for f in self.faculties:
                if f.name == faculty_name:
                    self.departments = self.controller.get_departments_by_faculty(f.id)
                    self.dept_combo['values'] = ['Tümü'] + [d.name for d in self.departments]
                    break
        self.dept_var.set('Tümü')
    
    def _get_selected_faculty_id(self):
        faculty_name = self.faculty_var.get()
        if faculty_name == 'Tümü':
            return None
        for f in self.faculties:
            if f.name == faculty_name:
                return f.id
        return None
    
    def _get_selected_department_id(self):
        dept_name = self.dept_var.get()
        if dept_name == 'Tümü':
            return None
        for d in self.departments:
            if d.name == dept_name:
                return d.id
        return None
    
    def _generate(self):
        faculty_id = self._get_selected_faculty_id()
        department_id = self._get_selected_department_id()
        
        data = self.controller.get_exams_by_faculty_or_department(faculty_id, department_id)
        
        if not data:
            messagebox.showinfo('Bilgi', 'Seçilen kriterlere uygun sınav bulunamadı.')
            return
        
        faculty_name = self.faculty_var.get()
        dept_name = self.dept_var.get()
        
        if dept_name != 'Tümü':
            filename_prefix = f'sinav_programi_{dept_name.replace(" ", "_").lower()}'
        elif faculty_name != 'Tümü':
            filename_prefix = f'sinav_programi_{faculty_name.replace(" ", "_").lower()}'
        else:
            filename_prefix = 'sinav_programi_tumu'
        
        self._export_excel(data, filename_prefix)
