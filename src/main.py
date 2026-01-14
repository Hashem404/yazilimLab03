import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.views.login_view import LoginView
from src.views.dashboard_view import DashboardView
from src.controllers.auth_controller import AuthController

class Application(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.title('Üniversite Sınav Programı Sistemi')
        self.geometry('1400x800')
        self.minsize(1200, 700)
        
        self._center_window()
        
        self._setup_styles()
        
        # Controller
        self.auth_controller = AuthController()
        
        # Ana container
        self.container = tk.Frame(self)
        self.container.pack(fill='both', expand=True)
        
        # İlk olarak login ekranını göster
        self.current_view = None
        self.show_login()
    
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (700)
        y = (self.winfo_screenheight() // 2) - (400)
        self.geometry(f'1400x800+{x}+{y}')
    
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Buton stilleri
        style.configure('Primary.TButton', 
                       background='#3498db', 
                       foreground='white',
                       padding=(20, 10),
                       font=('Segoe UI', 10))
        
        style.configure('Success.TButton',
                       background='#27ae60',
                       foreground='white',
                       padding=(15, 8),
                       font=('Segoe UI', 10))
        
        style.configure('Danger.TButton',
                       background='#e74c3c',
                       foreground='white',
                       padding=(15, 8),
                       font=('Segoe UI', 10))
        
        # Treeview stilleri
        style.configure('Treeview',
                       background='white',
                       foreground='#2c3e50',
                       rowheight=30,
                       fieldbackground='white',
                       font=('Segoe UI', 10))
        
        style.configure('Treeview.Heading',
                       background='#3498db',
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('Treeview',
                 background=[('selected', '#3498db')],
                 foreground=[('selected', 'white')])
    
    def show_login(self):
        self._clear_container()
        self.current_view = LoginView(self.container, on_login_success=self.on_login_success)
        self.current_view.set_auth_controller(self.auth_controller)
        self.current_view.pack(fill='both', expand=True)
    
    def show_dashboard(self):
        self._clear_container()
        self.current_view = DashboardView(self.container, self)
        self.current_view.pack(fill='both', expand=True)
    
    def _clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()
    
    def on_login_success(self):
        self.show_dashboard()
    
    def run(self):
        self.mainloop()


def main():
    try:
        app = Application()
        app.run()
    except Exception as e:
        messagebox.showerror('Hata', f'Uygulama başlatılamadı:\n{str(e)}')
        raise


if __name__ == '__main__':
    main()
