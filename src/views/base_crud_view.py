"""
Base CRUD View - Temel CRUD Görünümü
Tüm CRUD ekranları için ortak yapı sağlar
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.views.components.data_table import DataTable


class BaseCrudView(tk.Frame):
    title = "Veri Yönetimi"
    columns = []  # [('id', 'ID', 50), ('name', 'Ad', 150), ...]
    
    def __init__(self, parent, dashboard):
        super().__init__(parent, bg='#ecf0f1')
        self.dashboard = dashboard
        self.controller = dashboard.controller
        
        self._create_widgets()
        self.load_data()
    
    def _create_widgets(self):
        self._create_header()
        
        self._create_search_bar()
        
        self._create_data_table()
    
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
    
    def _create_data_table(self):
        table_frame = tk.Frame(self, bg='white', bd=1, relief='solid')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.data_table = DataTable(
            table_frame,
            columns=self.columns,
            on_select=self._on_select,
            on_double_click=self._on_double_click
        )
        self.data_table.pack(fill='both', expand=True)
    
    def _add_button_hover(self, btn, normal_color, hover_color):
        btn.bind('<Enter>', lambda e: btn.config(bg=hover_color))
        btn.bind('<Leave>', lambda e: btn.config(bg=normal_color))
    
    # ==================== Override edilecek metodlar ====================
    
    def load_data(self):
        """Veriyi yükler - Alt sınıflar tarafından override edilecek"""
        pass
    
    def get_form_fields(self):
        """
        Form alanlarını döndürür
        Returns: [{'name': 'field_name', 'label': 'Alan Adı', 'type': 'entry|combo|text', 
                   'required': True, 'options': [...]}]
        """
        return []
    
    def validate_form(self, data):
        """
        Form verilerini doğrular
        Returns: (bool, str) - (geçerli mi, hata mesajı)
        """
        return True, ""
    
    def create_item(self, data):
        """Yeni öğe oluşturur - Alt sınıflar tarafından override edilecek"""
        pass
    
    def update_item(self, id, data):
        """Öğe günceller - Alt sınıflar tarafından override edilecek"""
        pass
    
    def delete_item(self, id):
        """Öğe siler - Alt sınıflar tarafından override edilecek"""
        pass
    
    # ==================== Event handler'lar ====================
    
    def _on_search(self, *args):
        search_term = self.search_var.get().lower()
        self.load_data(search_term)
    
    def _on_select(self, item):
        pass
    
    def _on_double_click(self, item):
        if item:
            self._on_edit()
    
    def _on_add(self):
        self._show_form_dialog(mode='add')
    
    def _on_edit(self):
        selected = self.data_table.get_selected()
        if not selected:
            messagebox.showwarning('Uyarı', 'Lütfen düzenlemek için bir kayıt seçin.')
            return
        self._show_form_dialog(mode='edit', data=selected)
    
    def _on_delete(self):
        selected = self.data_table.get_selected()
        if not selected:
            messagebox.showwarning('Uyarı', 'Lütfen silmek için bir kayıt seçin.')
            return
        
        confirm = messagebox.askyesno(
            'Silme Onayı',
            'Bu kaydı silmek istediğinize emin misiniz?'
        )
        
        if confirm:
            result = self.delete_item(selected.get('id'))
            if result and result.get('success'):
                messagebox.showinfo('Başarılı', 'Kayıt silindi.')
                self.load_data()
            else:
                messagebox.showerror('Hata', result.get('message', 'Silme işlemi başarısız.'))
    
    def _show_form_dialog(self, mode='add', data=None):
        dialog = FormDialog(
            self,
            title='Yeni Ekle' if mode == 'add' else 'Düzenle',
            fields=self.get_form_fields(),
            data=data,
            on_save=lambda d: self._save_form(mode, data, d)
        )
        dialog.grab_set()
    
    def _save_form(self, mode, old_data, new_data):
        valid, error = self.validate_form(new_data)
        if not valid:
            messagebox.showerror('Doğrulama Hatası', error)
            return False
        
        if mode == 'add':
            result = self.create_item(new_data)
        else:
            result = self.update_item(old_data.get('id'), new_data)
        
        if result and result.get('success'):
            messagebox.showinfo('Başarılı', result.get('message', 'İşlem başarılı.'))
            self.load_data()
            return True
        else:
            messagebox.showerror('Hata', result.get('message', 'İşlem başarısız.'))
            return False


class FormDialog(tk.Toplevel):    
    def __init__(self, parent, title, fields, data=None, on_save=None):
        super().__init__(parent)
        self.fields = fields
        self.data = data or {}
        self.on_save = on_save
        self.field_vars = {}
        
        self.title(title)
        self.geometry('500x600')
        self.resizable(True, True)
        self.configure(bg='#ecf0f1')
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f'+{x}+{y}')
        
        self._create_widgets()
    
    def _create_widgets(self):
        canvas = tk.Canvas(self, bg='#ecf0f1', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        self.form_frame = tk.Frame(canvas, bg='#ecf0f1')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.create_window((0, 0), window=self.form_frame, anchor='nw')
        
        self.form_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        for field in self.fields:
            self._create_field(field)
        
        btn_frame = tk.Frame(self.form_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', pady=20, padx=20)
        
        save_btn = tk.Button(
            btn_frame,
            text='💾 Kaydet',
            font=('Segoe UI', 11),
            bg='#27ae60',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self._save
        )
        save_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(
            btn_frame,
            text='❌ İptal',
            font=('Segoe UI', 11),
            bg='#95a5a6',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.destroy
        )
        cancel_btn.pack(side='left', padx=5)
    
    def _create_field(self, field):
        frame = tk.Frame(self.form_frame, bg='#ecf0f1')
        frame.pack(fill='x', pady=8, padx=20)
        
        label_text = field['label']
        if field.get('required', False):
            label_text += ' *'
        
        label = tk.Label(
            frame,
            text=label_text,
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            fg='#2c3e50',
            anchor='w'
        )
        label.pack(fill='x')
        
        field_type = field.get('type', 'entry')
        field_name = field['name']
        default_value = self.data.get(field_name, field.get('default', ''))
        
        if field_type == 'entry':
            var = tk.StringVar(value=str(default_value) if default_value else '')
            entry = tk.Entry(
                frame,
                textvariable=var,
                font=('Segoe UI', 11),
                bd=1,
                relief='solid'
            )
            entry.pack(fill='x', ipady=5)
            self.field_vars[field_name] = var
            
        elif field_type == 'combo':
            var = tk.StringVar(value=str(default_value) if default_value else '')
            combo = ttk.Combobox(
                frame,
                textvariable=var,
                font=('Segoe UI', 11),
                state='readonly' if not field.get('editable', False) else 'normal'
            )
            options = field.get('options', [])
            combo['values'] = [opt[1] if isinstance(opt, tuple) else opt for opt in options]
            
            if default_value:
                for opt in options:
                    if isinstance(opt, tuple) and opt[0] == default_value:
                        var.set(opt[1])
                        break
                    elif opt == default_value:
                        var.set(opt)
                        break
            
            combo.pack(fill='x', ipady=3)
            self.field_vars[field_name] = var
            self.field_vars[f'{field_name}_options'] = options
            
        elif field_type == 'text':
            text = tk.Text(
                frame,
                font=('Segoe UI', 11),
                height=4,
                bd=1,
                relief='solid'
            )
            if default_value:
                text.insert('1.0', str(default_value))
            text.pack(fill='x')
            self.field_vars[field_name] = text
            
        elif field_type == 'spinbox':
            try:
                if default_value is not None and default_value != '':
                    int_value = int(default_value)
                else:
                    int_value = field.get('default', field.get('min', 0))
            except (ValueError, TypeError):
                import re
                numbers = re.findall(r'\d+', str(default_value))
                int_value = int(numbers[0]) if numbers else field.get('default', field.get('min', 0))
            
            var = tk.IntVar(value=int_value)
            spinbox = tk.Spinbox(
                frame,
                textvariable=var,
                font=('Segoe UI', 11),
                from_=field.get('min', 0),
                to=field.get('max', 1000),
                bd=1,
                relief='solid'
            )
            spinbox.pack(fill='x', ipady=5)
            self.field_vars[field_name] = var
            
        elif field_type == 'checkbox':
            var = tk.BooleanVar(value=bool(default_value))
            check = tk.Checkbutton(
                frame,
                variable=var,
                bg='#ecf0f1',
                activebackground='#ecf0f1'
            )
            check.pack(anchor='w')
            self.field_vars[field_name] = var
        
        elif field_type == 'multi_checkbox':
            options = field.get('options', [])
            checkbox_frame = tk.Frame(frame, bg='#ecf0f1')
            checkbox_frame.pack(fill='x', pady=5)
            
            checkbox_vars = {}
            
            default_list = default_value if isinstance(default_value, list) else field.get('default', [])
            
            for i, option in enumerate(options):
                var = tk.BooleanVar(value=(option in default_list))
                checkbox_vars[option] = var
                cb = tk.Checkbutton(
                    checkbox_frame,
                    text=option,
                    variable=var,
                    bg='#ecf0f1',
                    activebackground='#ecf0f1',
                    font=('Segoe UI', 9)
                )
                cb.grid(row=0, column=i, padx=5, pady=2, sticky='w')
            
            self.field_vars[field_name] = checkbox_vars
            self.field_vars[f'{field_name}_type'] = 'multi_checkbox'
            
        elif field_type == 'multi_combo':
            options = field.get('options', [])  # [(id, text), ...]
            
            hint_label = tk.Label(
                frame,
                text='(Ctrl+Click ile birden fazla seçin)',
                font=('Segoe UI', 8),
                bg='#ecf0f1',
                fg='#95a5a6'
            )
            hint_label.pack(anchor='w')
            
            list_frame = tk.Frame(frame, bg='#ecf0f1')
            list_frame.pack(fill='x', pady=5)
            
            scrollbar = ttk.Scrollbar(list_frame, orient='vertical')
            scrollbar.pack(side='right', fill='y')
            
            listbox = tk.Listbox(
                list_frame,
                selectmode='extended', 
                font=('Segoe UI', 9),
                height=field.get('height', 5),
                yscrollcommand=scrollbar.set,
                exportselection=False,
                bd=1,
                relief='solid'
            )
            listbox.pack(side='left', fill='x', expand=True)
            scrollbar.config(command=listbox.yview)
            
            for opt_id, opt_text in options:
                listbox.insert('end', opt_text)
            
            if default_value:
                default_list = default_value if isinstance(default_value, list) else [default_value]
                for i, (opt_id, opt_text) in enumerate(options):
                    if opt_id in default_list:
                        listbox.selection_set(i)
            
            self.field_vars[field_name] = listbox
            self.field_vars[f'{field_name}_options'] = options
            self.field_vars[f'{field_name}_type'] = 'multi_combo'
            
        elif field_type == 'date':
            var = tk.StringVar(value=str(default_value) if default_value else '')
            entry = tk.Entry(
                frame,
                textvariable=var,
                font=('Segoe UI', 11),
                bd=1,
                relief='solid'
            )
            entry.pack(fill='x', ipady=5)
            
            hint = tk.Label(
                frame,
                text='Format: YYYY-MM-DD',
                font=('Segoe UI', 8),
                bg='#ecf0f1',
                fg='#95a5a6'
            )
            hint.pack(anchor='w')
            self.field_vars[field_name] = var
            
        elif field_type == 'time':
            var = tk.StringVar(value=str(default_value) if default_value else '')
            entry = tk.Entry(
                frame,
                textvariable=var,
                font=('Segoe UI', 11),
                bd=1,
                relief='solid'
            )
            entry.pack(fill='x', ipady=5)
            
            hint = tk.Label(
                frame,
                text='Format: HH:MM',
                font=('Segoe UI', 8),
                bg='#ecf0f1',
                fg='#95a5a6'
            )
            hint.pack(anchor='w')
            self.field_vars[field_name] = var
    
    def _get_form_data(self):
        data = {}
        for field in self.fields:
            field_name = field['name']
            field_type = field.get('type', 'entry')
            
            if field_type == 'text':
                widget = self.field_vars[field_name]
                data[field_name] = widget.get('1.0', 'end-1c').strip()
            elif field_type == 'combo':
                var = self.field_vars[field_name]
                value = var.get()
                options = self.field_vars.get(f'{field_name}_options', [])
                
                for opt in options:
                    if isinstance(opt, tuple) and opt[1] == value:
                        data[field_name] = opt[0]
                        break
                else:
                    data[field_name] = value
            elif field_type == 'spinbox':
                data[field_name] = self.field_vars[field_name].get()
            elif field_type == 'checkbox':
                data[field_name] = self.field_vars[field_name].get()
            elif field_type == 'multi_checkbox':
                checkbox_vars = self.field_vars[field_name]
                data[field_name] = [option for option, var in checkbox_vars.items() if var.get()]
            elif field_type == 'multi_combo':
                listbox = self.field_vars[field_name]
                options = self.field_vars.get(f'{field_name}_options', [])
                selected_indices = listbox.curselection()
                data[field_name] = [options[i][0] for i in selected_indices if i < len(options)]
            else:
                data[field_name] = self.field_vars[field_name].get().strip()
        
        return data
    
    def _save(self):
        data = self._get_form_data()
        
        for field in self.fields:
            if field.get('required', False):
                field_name = field['name']
                field_type = field.get('type', 'entry')
                value = data.get(field_name)
                
                if field_type in ('multi_checkbox', 'multi_combo'):
                    if not value or len(value) == 0:
                        messagebox.showerror(
                            'Zorunlu Alan',
                            f"'{field['label']}' alanında en az bir seçim yapılmalıdır."
                        )
                        return
                elif not value:
                    messagebox.showerror(
                        'Zorunlu Alan',
                        f"'{field['label']}' alanı zorunludur."
                    )
                    return
        
        if self.on_save:
            success = self.on_save(data)
            if success:
                self.destroy()
