"""
Giriş ekranı view - Modern ve kullanıcı dostu tasarım
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from src.views.student_schedule_view import StudentScheduleView


class LoginView(tk.Frame):
    """Kullanıcı giriş ekranı"""
    
    COLORS = {
        'primary': '#3498db',
        'primary_dark': '#2980b9',
        'secondary': '#2c3e50',
        'background': '#ecf0f1',
        'card_bg': '#ffffff',
        'text': '#2c3e50',
        'text_light': '#7f8c8d',
        'error': '#e74c3c',
        'success': '#27ae60',
    }
    
    def __init__(self, parent, on_login_success: Callable = None):
        super().__init__(parent, bg=self.COLORS['background'])
        self.on_login_success = on_login_success
        self._auth_controller = None
        
        self._setup_styles()
        self._create_widgets()
        self._setup_bindings()
    
    def set_auth_controller(self, controller):
        self._auth_controller = controller
    
    def _setup_styles(self):
        style = ttk.Style()
        
        style.configure(
            'Login.TEntry',
            padding=10,
            font=('Segoe UI', 11)
        )

        style.configure(
            'Login.TLabel',
            background=self.COLORS['card_bg'],
            foreground=self.COLORS['text'],
            font=('Segoe UI', 10)
        )
        
        style.configure(
            'LoginTitle.TLabel',
            background=self.COLORS['card_bg'],
            foreground=self.COLORS['secondary'],
            font=('Segoe UI', 20, 'bold')
        )
        
        style.configure(
            'LoginSubtitle.TLabel',
            background=self.COLORS['card_bg'],
            foreground=self.COLORS['text_light'],
            font=('Segoe UI', 10)
        )
        
        style.configure(
            'LoginError.TLabel',
            background=self.COLORS['card_bg'],
            foreground=self.COLORS['error'],
            font=('Segoe UI', 9)
        )
    
    def _create_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        card = tk.Frame(self, bg=self.COLORS['card_bg'], padx=40, pady=40)
        card.grid(row=0, column=0)
        
        card.config(
            highlightbackground='#bdc3c7',
            highlightthickness=1
        )
        
        logo_frame = tk.Frame(card, bg=self.COLORS['card_bg'])
        logo_frame.pack(pady=(0, 20))
        
        logo_label = tk.Label(
            logo_frame,
            text='🎓',
            font=('Segoe UI', 48),
            bg=self.COLORS['card_bg']
        )
        logo_label.pack()
        
        title_label = ttk.Label(
            card,
            text='Üniversite Sınav Programı',
            style='LoginTitle.TLabel'
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ttk.Label(
            card,
            text='Sınav Yönetim Sistemi',
            style='LoginSubtitle.TLabel'
        )
        subtitle_label.pack(pady=(0, 30))
        
        form_frame = tk.Frame(card, bg=self.COLORS['card_bg'])
        form_frame.pack(fill='x')
        
        username_label = ttk.Label(
            form_frame,
            text='Kullanıcı Adı',
            style='Login.TLabel'
        )
        username_label.pack(anchor='w')
        
        self.username_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='#ffffff',
            fg=self.COLORS['text'],
            insertbackground=self.COLORS['text'],
            relief='solid',
            bd=1,
            highlightthickness=2,
            highlightcolor=self.COLORS['primary'],
            highlightbackground='#bdc3c7'
        )
        self.username_entry.pack(fill='x', pady=(5, 15), ipady=8)
        
        password_label = ttk.Label(
            form_frame,
            text='Şifre',
            style='Login.TLabel'
        )
        password_label.pack(anchor='w')
        
        self.password_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg='#ffffff',
            fg=self.COLORS['text'],
            insertbackground=self.COLORS['text'],
            relief='solid',
            bd=1,
            show='•',
            highlightthickness=2,
            highlightcolor=self.COLORS['primary'],
            highlightbackground='#bdc3c7'
        )
        self.password_entry.pack(fill='x', pady=(5, 20), ipady=8)
        
        self.error_frame = tk.Frame(form_frame, bg=self.COLORS['card_bg'])
        self.error_frame.pack(fill='x', pady=(0, 10))
        
        self.error_label = ttk.Label(
            self.error_frame,
            text='',
            style='LoginError.TLabel'
        )
        self.error_label.pack()
        
        self.login_btn = tk.Button(
            form_frame,
            text='Giriş Yap',
            font=('Segoe UI', 11, 'bold'),
            bg=self.COLORS['primary'],
            fg='white',
            activebackground=self.COLORS['primary_dark'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            command=self._on_login_click,
            pady=10
        )
        self.login_btn.pack(fill='x', pady=(0, 20))
        
        self.login_btn.bind('<Enter>', lambda e: self.login_btn.config(bg=self.COLORS['primary_dark']))
        self.login_btn.bind('<Leave>', lambda e: self.login_btn.config(bg=self.COLORS['primary']))
        
        footer_label = tk.Label(
            card,
            text='2025 Üniversite Sınav Yönetim Sistemi',
            font=('Segoe UI', 8),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_light']
        )
        footer_label.pack(pady=(10, 0))
    
    def _setup_bindings(self):
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self._on_login_click())
        
        self.username_entry.bind('<FocusIn>', lambda e: self.username_entry.config(highlightbackground=self.COLORS['primary']))
        self.username_entry.bind('<FocusOut>', lambda e: self.username_entry.config(highlightbackground='#bdc3c7'))
        self.password_entry.bind('<FocusIn>', lambda e: self.password_entry.config(highlightbackground=self.COLORS['primary']))
        self.password_entry.bind('<FocusOut>', lambda e: self.password_entry.config(highlightbackground='#bdc3c7'))
        
        self.after(100, lambda: self.username_entry.focus())
    
    def _on_login_click(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self._show_error('Kullanıcı adı ve şifre gereklidir.')
            return
        
        self._clear_error()
        
        self.login_btn.config(text='Giriş yapılıyor...', state='disabled')
        self.update()
        
        if self._auth_controller:
            result = self._auth_controller.login(username, password)
            success = result.get('success', False)
            message = result.get('message', '')
            if success:
                user_info = result.get('user') or {}
                role = (user_info.get('role') or user_info.get('user_type') or '').lower()
                if role in ('student', 'ogrenci'):
                    self._open_student_schedule(user_info)
                    return
                if self.on_login_success:
                    self.on_login_success()
            else:
                self._show_error(message)
                self.login_btn.config(text='Giriş Yap', state='normal')
        else:
            self._show_error('Sistem hatası: Controller bulunamadı.')
            self.login_btn.config(text='Giriş Yap', state='normal')

    def _open_student_schedule(self, user_info: dict):
        student_id = user_info.get('student_id') or user_info.get('id')
        if not student_id:
            self._show_error('Öğrenci bilgisi bulunamadı.')
            self.login_btn.config(text='Giriş Yap', state='normal')
            return
        
        try:
            StudentScheduleView(self.winfo_toplevel(), student_id=student_id)
        except Exception as exc:
            messagebox.showerror('Hata', f'Öğrenci programı açılamadı: {str(exc)}')
        finally:
            self.login_btn.config(text='Giriş Yap', state='normal')
    
    def _show_error(self, message: str):
        self.error_label.config(text=f'⚠ {message}')
        self.username_entry.config(highlightbackground=self.COLORS['error'])
        self.password_entry.config(highlightbackground=self.COLORS['error'])
    
    def _clear_error(self):
        self.error_label.config(text='')
        self.username_entry.config(highlightbackground='#bdc3c7')
        self.password_entry.config(highlightbackground='#bdc3c7')
    
    def clear_form(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self._clear_error()
        self.login_btn.config(text='Giriş Yap', state='normal')
        self.username_entry.focus()
