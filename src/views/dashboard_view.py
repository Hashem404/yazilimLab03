"""
Dashboard View - Ana Panel Görünümü
Sol menü ve içerik alanını yönetir
Rol bazlı içerik gösterimi sağlar
"""

import tkinter as tk
from tkinter import ttk
from src.views.components.sidebar import Sidebar
from src.controllers.dashboard_controller import DashboardController


class DashboardView(tk.Frame):    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app 
        self.controller = DashboardController(self)
        self.current_view = None
        
        self.user_info = self.app.auth_controller.get_current_user()
        self.user_role = self.user_info.get('role', 'ogrenci') if self.user_info else 'ogrenci'
        self.user_department_id = self.user_info.get('department_id') if self.user_info else None
        
        self._create_widgets()
        self._show_home()
    
    def _create_widgets(self):
        self.sidebar = Sidebar(self, on_menu_click=self._on_menu_click, user_role=self.user_role)
        self.sidebar.pack(side='left', fill='y')
        
        user_frame = tk.Frame(self.sidebar, bg='#1a252f')
        user_frame.pack(side='bottom', fill='x')
        
        if self.user_info:
            user_label = tk.Label(
                user_frame,
                text=f"👤 {self.user_info.get('username', '')}",
                font=('Segoe UI', 9),
                bg='#1a252f',
                fg='#bdc3c7'
            )
            user_label.pack(pady=5)
        
        logout_btn = tk.Button(
            user_frame,
            text='🚪 Çıkış',
            font=('Segoe UI', 10),
            bg='#c0392b',
            fg='white',
            bd=0,
            padx=10,
            pady=5,
            cursor='hand2',
            command=self._logout
        )
        logout_btn.pack(pady=10)
        
        self.content_frame = tk.Frame(self, bg='#ecf0f1')
        self.content_frame.pack(side='right', fill='both', expand=True)
    
    def _on_menu_click(self, key, view_name):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.current_view = None
        
        if key == 'dashboard':
            self._show_home()
        elif key == 'faculties':
            if self.user_role == 'admin':
                from src.views.faculty_view import FacultyView
                self.current_view = FacultyView(self.content_frame, self)
        elif key == 'departments':
            if self.user_role == 'admin':
                from src.views.department_view import DepartmentView
                self.current_view = DepartmentView(self.content_frame, self)
        elif key == 'classrooms':
            if self.user_role == 'admin':
                from src.views.classroom_view import ClassroomView
                self.current_view = ClassroomView(self.content_frame, self)
        elif key == 'lecturers':
            if self.user_role in ['admin', 'bolum_yetkilisi']:
                from src.views.lecturer_view import LecturerView
                self.current_view = LecturerView(self.content_frame, self)
        elif key == 'courses':
            if self.user_role in ['admin', 'bolum_yetkilisi']:
                from src.views.course_view import CourseView
                self.current_view = CourseView(self.content_frame, self)
        elif key == 'import_view':
            if self.user_role in ['admin', 'bolum_yetkilisi']:
                from src.views.import_view import ImportView
                self.current_view = ImportView(self.content_frame, self)
        elif key == 'student_lists':
            if self.user_role in ['admin', 'bolum_yetkilisi']:
                from src.views.course_view import CourseView
                self.current_view = CourseView(self.content_frame, self)
        elif key == 'schedule':
            from src.views.exam_schedule_view import ExamScheduleView
            self.current_view = ExamScheduleView(self.content_frame, self)
        elif key == 'reports':
            if self.user_role == 'admin':
                from src.views.reports_view import ReportsView
                self.current_view = ReportsView(self.content_frame, self)
        
        if self.current_view:
            self.current_view.pack(fill='both', expand=True)
    
    def _show_home(self):
        if self.user_role == 'admin':
            self._show_admin_home()
        elif self.user_role == 'bolum_yetkilisi':
            self._show_bolum_yetkilisi_home()
        elif self.user_role == 'hoca':
            self._show_hoca_home()
        elif self.user_role == 'ogrenci':
            self._show_ogrenci_home()
        else:
            self._show_admin_home()
    
    def _show_admin_home(self):
        home_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        home_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        title = tk.Label(
            home_frame,
            text='📊 Sistem Özeti (Admin)',
            font=('Segoe UI', 24, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        title.pack(anchor='w', pady=(0, 30))
        
        stats_frame = tk.Frame(home_frame, bg='#ecf0f1')
        stats_frame.pack(fill='x')
        
        stats = [
            ('🏛️ Fakülteler', len(self.controller.get_all_faculties()), '#3498db'),
            ('📚 Bölümler', len(self.controller.get_all_departments()), '#9b59b6'),
            ('🚪 Derslikler', len(self.controller.get_all_classrooms()), '#1abc9c'),
            ('👨‍🏫 Öğretim Üyeleri', len(self.controller.get_all_lecturers()), '#e67e22'),
            ('📖 Dersler', len(self.controller.get_all_courses()), '#e74c3c'),
            ('📅 Planlanan Sınavlar', len(self.controller.get_all_exams()), '#2ecc71'),
        ]
        
        for i, (label, count, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=color, padx=20, pady=20)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='nsew')
            
            count_label = tk.Label(
                card, 
                text=str(count), 
                font=('Segoe UI', 36, 'bold'), 
                bg=color, 
                fg='white'
            )
            count_label.pack()
            
            text_label = tk.Label(
                card, 
                text=label, 
                font=('Segoe UI', 12), 
                bg=color, 
                fg='white'
            )
            text_label.pack()
        
        for i in range(3):
            stats_frame.columnconfigure(i, weight=1)
        
        self._show_upcoming_exams(home_frame)
    
    def _show_bolum_yetkilisi_home(self):
        home_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        home_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        department_name = "Bölümünüz"
        if self.user_department_id:
            departments = self.controller.get_all_departments()
            for dept in departments:
                if dept.id == self.user_department_id:
                    department_name = dept.name
                    break
        
        title = tk.Label(
            home_frame,
            text=f'📊 {department_name} - Bölüm Özeti',
            font=('Segoe UI', 24, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        title.pack(anchor='w', pady=(0, 30))
        
        stats_frame = tk.Frame(home_frame, bg='#ecf0f1')
        stats_frame.pack(fill='x')
        
        all_lecturers = self.controller.get_all_lecturers()
        dept_lecturers = [l for l in all_lecturers if l.department_id == self.user_department_id]
        
        all_courses = self.controller.get_all_courses()
        dept_courses = [c for c in all_courses if c.department_id == self.user_department_id]
        
        all_exams = self.controller.get_all_exams()
        dept_course_ids = [c.id for c in dept_courses]
        dept_exams = [e for e in all_exams if e.course_id in dept_course_ids]
        
        stats = [
            ('👨‍🏫 Öğretim Üyeleri', len(dept_lecturers), '#e67e22'),
            ('📖 Dersler', len(dept_courses), '#e74c3c'),
            ('📅 Planlanan Sınavlar', len(dept_exams), '#2ecc71'),
        ]
        
        for i, (label, count, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=color, padx=20, pady=20)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            
            count_label = tk.Label(
                card, 
                text=str(count), 
                font=('Segoe UI', 36, 'bold'), 
                bg=color, 
                fg='white'
            )
            count_label.pack()
            
            text_label = tk.Label(
                card, 
                text=label, 
                font=('Segoe UI', 12), 
                bg=color, 
                fg='white'
            )
            text_label.pack()
        
        for i in range(3):
            stats_frame.columnconfigure(i, weight=1)
        
        info_label = tk.Label(
            home_frame,
            text='ℹ️ Bölüm yetkilisi olarak sadece kendi bölümünüze ait öğretim üyelerini, dersleri ve sınav programını yönetebilirsiniz.',
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            fg='#7f8c8d',
            wraplength=600
        )
        info_label.pack(anchor='w', pady=(20, 0))
        
        self._show_upcoming_exams(home_frame, department_filter=self.user_department_id)
    
    def _show_hoca_home(self):
        """Hoca için ana sayfa - sadece kendi derslerinin sınav programını görüntüleme"""
        home_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        home_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        lecturer_name = self.user_info.get('full_name') or self.user_info.get('username') if self.user_info else "Hoca"
        
        title = tk.Label(
            home_frame,
            text=f'📅 Sınav Programınız - {lecturer_name}',
            font=('Segoe UI', 24, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        title.pack(anchor='w', pady=(0, 30))
        
        info_label = tk.Label(
            home_frame,
            text='ℹ️ Öğretim üyesi olarak verdiğiniz derslerin sınav programını buradan görüntüleyebilirsiniz. Listede sadece kendi derslerinizin sınavları gösterilmektedir.',
            font=('Segoe UI', 11),
            bg='#ecf0f1',
            fg='#2c3e50',
            wraplength=600
        )
        info_label.pack(anchor='w', pady=(0, 20))
        
        # Kullanıcı bazlı filtreleme ile sınavları göster
        self._show_upcoming_exams(home_frame, use_user_filter=True)
    
    def _show_ogrenci_home(self):
        """Öğrenci için ana sayfa - sadece aldığı derslerin sınav programı görüntüleme"""
        home_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        home_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        student_name = self.user_info.get('full_name') or self.user_info.get('username') if self.user_info else "Öğrenci"
        
        title = tk.Label(
            home_frame,
            text=f'📅 Sınav Programınız - {student_name}',
            font=('Segoe UI', 24, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        title.pack(anchor='w', pady=(0, 30))
        
        info_label = tk.Label(
            home_frame,
            text='ℹ️ Öğrenci olarak kayıtlı olduğunuz derslerin sınav programını buradan görüntüleyebilirsiniz. Listede sadece aldığınız derslerin sınavları gösterilmektedir.',
            font=('Segoe UI', 11),
            bg='#ecf0f1',
            fg='#2c3e50',
            wraplength=600
        )
        info_label.pack(anchor='w', pady=(0, 20))
        
        # Kullanıcı bazlı filtreleme ile sınavları göster
        self._show_upcoming_exams(home_frame, use_user_filter=True)
    
    def _show_upcoming_exams(self, parent, department_filter=None, use_user_filter=False):
        """
        Kullanıcı bazlı sınav gösterimi.
        
        Args:
            parent: Ebeveyn widget
            department_filter: Bölüm filtresi (eski yöntem, backward compatibility)
            use_user_filter: Kullanıcı bazlı filtreleme kullan
        """
        upcoming_title = tk.Label(
            parent,
            text='📅 Yaklaşan Sınavlar',
            font=('Segoe UI', 18, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        upcoming_title.pack(anchor='w', pady=(30, 15))
        
        exams_frame = tk.Frame(parent, bg='white', bd=1, relief='solid')
        exams_frame.pack(fill='x')
        
        # Kullanıcı bazlı filtreleme
        if use_user_filter and self.user_info:
            upcoming = self.controller.filter_schedule_by_user(self.user_info)
        else:
            upcoming = self.controller.get_upcoming_exams(days=7)
            
            if department_filter:
                all_courses = self.controller.get_all_courses()
                dept_course_ids = [c.id for c in all_courses if c.department_id == department_filter]
                upcoming = [e for e in upcoming if e.get('course_id') in dept_course_ids]
        
        if not upcoming:
            no_exam_label = tk.Label(
                exams_frame,
                text='Yaklaşan sınav bulunmamaktadır.',
                font=('Segoe UI', 11),
                bg='white',
                fg='#7f8c8d',
                pady=20
            )
            no_exam_label.pack()
        else:
            for exam in upcoming[:5]:
                exam_row = tk.Frame(exams_frame, bg='white', pady=8, padx=15)
                exam_row.pack(fill='x', padx=1, pady=1)
                
                date_label = tk.Label(
                    exam_row,
                    text=f"📆 {exam['date']}",
                    font=('Segoe UI', 10),
                    bg='white',
                    fg='#3498db',
                    width=12,
                    anchor='w'
                )
                date_label.pack(side='left')
                
                time_label = tk.Label(
                    exam_row,
                    text=f"⏰ {exam['time']}",
                    font=('Segoe UI', 10),
                    bg='white',
                    fg='#e67e22',
                    width=10,
                    anchor='w'
                )
                time_label.pack(side='left')
                
                course_label = tk.Label(
                    exam_row,
                    text=f"{exam['course_code']} - {exam['course_name']}",
                    font=('Segoe UI', 10, 'bold'),
                    bg='white',
                    fg='#2c3e50',
                    anchor='w'
                )
                course_label.pack(side='left', fill='x', expand=True)
                
                room_label = tk.Label(
                    exam_row,
                    text=f"📍 {exam['classroom']}",
                    font=('Segoe UI', 10),
                    bg='white',
                    fg='#7f8c8d'
                )
                room_label.pack(side='right')
    
    def _logout(self):
        self.app.auth_controller.logout()
        self.app.show_login()
    
    def refresh(self):
        self._on_menu_click('dashboard', 'DashboardView')
    
    def get_user_department_id(self):
        return self.user_department_id
    
    def get_user_role(self):
        return self.user_role
