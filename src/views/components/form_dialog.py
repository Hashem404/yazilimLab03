"""
Form Dialog Bileşeni
Modal dialog - ekleme/düzenleme formları için
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Callable, List


class FormDialog(tk.Toplevel):
    
    def __init__(self, parent, title: str, fields: List[Dict[str, Any]], 
                 on_submit: Callable[[Dict[str, Any]], bool],
                 initial_data: Optional[Dict[str, Any]] = None,
                 width: int = 500, height: int = 400):

        super().__init__(parent)
        
        self.title(title)
        self.fields = fields
        self.on_submit = on_submit
        self.initial_data = initial_data or {}
        self.result = None
        
        self.transient(parent)
        self.grab_set()
        
        self.geometry(f'{width}x{height}')
        self.resizable(True, True)
        self.minsize(400, 300)
        
        self._center_window(parent, width, height)
        
        self.widgets: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        
        self._create_ui()
        
        self.bind('<Escape>', lambda e: self._on_cancel())
        
        self.protocol('WM_DELETE_WINDOW', self._on_cancel)
    
    def _center_window(self, parent, width: int, height: int):
        parent.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_ui(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        
        self.form_frame = ttk.Frame(canvas)
        
        self.form_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.form_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        
        canvas.bind_all('<MouseWheel>', _on_mousewheel)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self._create_fields()
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        cancel_btn = ttk.Button(
            button_frame,
            text='İptal',
            command=self._on_cancel,
            style='Danger.TButton'
        )
        cancel_btn.pack(side='right', padx=(10, 0))
        
        save_btn = ttk.Button(
            button_frame,
            text='Kaydet',
            command=self._on_save,
            style='Success.TButton'
        )
        save_btn.pack(side='right')
    
    def _create_fields(self):
        for i, field in enumerate(self.fields):
            field_name = field['name']
            field_label = field.get('label', field_name)
            field_type = field.get('type', 'entry')
            required = field.get('required', False)
            
            label_text = f"{field_label}{'*' if required else ''}"
            label = ttk.Label(self.form_frame, text=label_text, font=('Segoe UI', 10))
            label.grid(row=i, column=0, sticky='w', padx=(0, 10), pady=5)
            
            widget = self._create_field_widget(field)
            widget.grid(row=i, column=1, sticky='ew', pady=5)
            
            self.widgets[field_name] = widget
            
            if field_name in self.initial_data:
                self._set_field_value(field_name, field_type, self.initial_data[field_name])
            elif 'default' in field:
                self._set_field_value(field_name, field_type, field['default'])
        
        self.form_frame.columnconfigure(1, weight=1)
    
    def _create_field_widget(self, field: Dict[str, Any]) -> tk.Widget:
        field_name = field['name']
        field_type = field.get('type', 'entry')
        
        if field_type == 'entry':
            var = tk.StringVar()
            self.variables[field_name] = var
            widget = ttk.Entry(self.form_frame, textvariable=var, font=('Segoe UI', 10))
            
        elif field_type == 'spinbox':
            var = tk.IntVar()
            self.variables[field_name] = var
            from_ = field.get('from_', 0)
            to = field.get('to', 100)
            widget = ttk.Spinbox(
                self.form_frame,
                from_=from_,
                to=to,
                textvariable=var,
                font=('Segoe UI', 10),
                width=18
            )
            
        elif field_type == 'combobox':
            var = tk.StringVar()
            self.variables[field_name] = var
            values = field.get('values', [])
            widget = ttk.Combobox(
                self.form_frame,
                textvariable=var,
                values=values,
                font=('Segoe UI', 10),
                state='readonly' if field.get('readonly', True) else 'normal'
            )
            
        elif field_type == 'text':
            widget = tk.Text(
                self.form_frame,
                height=field.get('height', 4),
                font=('Segoe UI', 10),
                wrap='word'
            )
            self.variables[field_name] = None
            
        elif field_type == 'checkbox':
            var = tk.BooleanVar()
            self.variables[field_name] = var
            widget = ttk.Checkbutton(
                self.form_frame,
                variable=var,
                text=field.get('checkbox_text', '')
            )
        
        elif field_type == 'multi_checkbox':
            options = field.get('options', [])
            frame = ttk.Frame(self.form_frame)
            
            checkbox_vars = {}
            for i, option in enumerate(options):
                var = tk.BooleanVar(value=True)
                checkbox_vars[option] = var
                cb = ttk.Checkbutton(
                    frame,
                    text=option,
                    variable=var
                )
                cb.grid(row=0, column=i, padx=5, pady=2, sticky='w')
            
            self.variables[field_name] = checkbox_vars
            return frame
            
        elif field_type == 'date':
            var = tk.StringVar()
            self.variables[field_name] = var
            frame = ttk.Frame(self.form_frame)
            widget = ttk.Entry(frame, textvariable=var, font=('Segoe UI', 10), width=12)
            widget.pack(side='left')
            hint_label = ttk.Label(frame, text='(YYYY-MM-DD)', font=('Segoe UI', 8), foreground='gray')
            hint_label.pack(side='left', padx=(5, 0))
            self.widgets[field_name + '_entry'] = widget
            return frame
            
        elif field_type == 'time':
            var = tk.StringVar()
            self.variables[field_name] = var
            frame = ttk.Frame(self.form_frame)
            widget = ttk.Entry(frame, textvariable=var, font=('Segoe UI', 10), width=8)
            widget.pack(side='left')
            hint_label = ttk.Label(frame, text='(HH:MM)', font=('Segoe UI', 8), foreground='gray')
            hint_label.pack(side='left', padx=(5, 0))
            self.widgets[field_name + '_entry'] = widget
            return frame
        
        elif field_type == 'combo':
            options = field.get('options', [])  
            var = tk.StringVar()
            self.variables[field_name] = var
            
            display_values = [opt[1] for opt in options]
            
            frame = ttk.Frame(self.form_frame)
            widget = ttk.Combobox(
                frame,
                textvariable=var,
                values=display_values,
                font=('Segoe UI', 10),
                state='readonly',
                width=35
            )
            widget.pack(side='left', fill='x', expand=True)
            
            # Options referansını sakla
            self.widgets[field_name + '_options'] = options
            self.widgets[field_name + '_combo'] = widget
            return frame
        
        elif field_type == 'multi_combo':
            options = field.get('options', [])
            
            frame = ttk.Frame(self.form_frame)
            
            hint_label = ttk.Label(
                frame,
                text='(Ctrl+Click ile birden fazla seçin)',
                font=('Segoe UI', 8),
                foreground='gray'
            )
            hint_label.pack(anchor='w')
            
            list_frame = ttk.Frame(frame)
            list_frame.pack(fill='both', expand=True)
            
            scrollbar = ttk.Scrollbar(list_frame, orient='vertical')
            scrollbar.pack(side='right', fill='y')
            
            listbox = tk.Listbox(
                list_frame,
                selectmode='extended', 
                font=('Segoe UI', 9),
                height=field.get('height', 5),
                yscrollcommand=scrollbar.set,
                exportselection=False
            )
            listbox.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=listbox.yview)
            
            for opt_id, opt_text in options:
                listbox.insert('end', opt_text)
            
            self.variables[field_name] = options 
            self.widgets[field_name + '_listbox'] = listbox
            
            return frame
            
        else:
            var = tk.StringVar()
            self.variables[field_name] = var
            widget = ttk.Entry(self.form_frame, textvariable=var, font=('Segoe UI', 10))
        
        return widget
    
    def _set_field_value(self, field_name: str, field_type: str, value: Any):
        if field_type == 'text':
            widget = self.widgets.get(field_name)
            if widget:
                widget.delete('1.0', 'end')
                if value:
                    widget.insert('1.0', str(value))
        elif field_type in ['date', 'time']:
            var = self.variables.get(field_name)
            if var and value:
                var.set(str(value))
        elif field_type == 'multi_checkbox':
            checkbox_vars = self.variables.get(field_name)
            if checkbox_vars and isinstance(value, list):
                for option, var in checkbox_vars.items():
                    var.set(option in value)
        elif field_type == 'combo':
            options = self.widgets.get(field_name + '_options', [])
            var = self.variables.get(field_name)
            if var and value is not None:
                for opt_id, opt_text in options:
                    if opt_id == value:
                        var.set(opt_text)
                        break
        elif field_type == 'multi_combo':
            listbox = self.widgets.get(field_name + '_listbox')
            options = self.variables.get(field_name, [])
            if listbox and value is not None:
                listbox.selection_clear(0, 'end')
                if isinstance(value, list):
                    for i, (opt_id, opt_text) in enumerate(options):
                        if opt_id in value:
                            listbox.selection_set(i)
                elif isinstance(value, int):
                    for i, (opt_id, opt_text) in enumerate(options):
                        if opt_id == value:
                            listbox.selection_set(i)
                            break
        else:
            var = self.variables.get(field_name)
            if var is not None and value is not None:
                var.set(value)
    
    def _get_field_value(self, field_name: str, field_type: str) -> Any:
        if field_type == 'text':
            widget = self.widgets.get(field_name)
            if widget:
                return widget.get('1.0', 'end-1c').strip()
            return ''
        elif field_type == 'spinbox':
            var = self.variables.get(field_name)
            if var:
                try:
                    return var.get()
                except tk.TclError:
                    return 0
            return 0
        elif field_type == 'checkbox':
            var = self.variables.get(field_name)
            if var:
                return var.get()
            return False
        elif field_type == 'multi_checkbox':
            checkbox_vars = self.variables.get(field_name)
            if checkbox_vars:
                return [option for option, var in checkbox_vars.items() if var.get()]
            return []
        elif field_type == 'combo':
            var = self.variables.get(field_name)
            options = self.widgets.get(field_name + '_options', [])
            if var:
                selected_text = var.get()
                for opt_id, opt_text in options:
                    if opt_text == selected_text:
                        return opt_id
            return None
        elif field_type == 'multi_combo':
            listbox = self.widgets.get(field_name + '_listbox')
            options = self.variables.get(field_name, [])
            if listbox:
                selected_indices = listbox.curselection()
                selected_ids = [options[i][0] for i in selected_indices if i < len(options)]
                return selected_ids
            return []
        else:
            var = self.variables.get(field_name)
            if var:
                return var.get()
            return ''
    
    def _validate_fields(self) -> tuple[bool, str]:
        for field in self.fields:
            field_name = field['name']
            field_label = field.get('label', field_name)
            field_type = field.get('type', 'entry')
            required = field.get('required', False)
            
            if required:
                value = self._get_field_value(field_name, field_type)
                
                if field_type == 'multi_combo':
                    if not value or len(value) == 0:
                        return False, f"'{field_label}' alanında en az bir seçim yapılmalıdır."
                elif field_type == 'combo':
                    if value is None:
                        return False, f"'{field_label}' alanı zorunludur."
                elif value is None or value == '' or (isinstance(value, str) and not value.strip()):
                    return False, f"'{field_label}' alanı zorunludur."
                
                if field_type == 'date' and value:
                    import re
                    if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                        return False, f"'{field_label}' alanı YYYY-MM-DD formatında olmalıdır."
                
                if field_type == 'time' and value:
                    import re
                    if not re.match(r'^\d{2}:\d{2}$', value):
                        return False, f"'{field_label}' alanı HH:MM formatında olmalıdır."
        
        return True, ''
    
    def get_data(self) -> Dict[str, Any]:
        data = {}
        for field in self.fields:
            field_name = field['name']
            field_type = field.get('type', 'entry')
            data[field_name] = self._get_field_value(field_name, field_type)
        return data
    
    def _on_save(self):
        is_valid, error_message = self._validate_fields()
        if not is_valid:
            from tkinter import messagebox
            messagebox.showwarning('Uyarı', error_message, parent=self)
            return
        
        data = self.get_data()
        
        try:
            if self.on_submit(data):
                self.result = data
                self.destroy()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror('Hata', f'Kaydetme hatası:\n{str(e)}', parent=self)
    
    def _on_cancel(self):
        self.result = None
        self.destroy()
    
    def show(self) -> Optional[Dict[str, Any]]:
        self.wait_window()
        return self.result


class ConfirmDialog(tk.Toplevel):
    
    def __init__(self, parent, title: str, message: str, 
                 confirm_text: str = 'Evet', cancel_text: str = 'Hayır'):
        super().__init__(parent)
        
        self.title(title)
        self.result = False
        
        self.transient(parent)
        self.grab_set()
        
        width, height = 400, 180
        self.geometry(f'{width}x{height}')
        self.resizable(False, False)
        
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        msg_label = ttk.Label(
            main_frame,
            text=message,
            wraplength=360,
            justify='center',
            font=('Segoe UI', 11)
        )
        msg_label.pack(expand=True)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        cancel_btn = ttk.Button(
            button_frame,
            text=cancel_text,
            command=self._on_cancel
        )
        cancel_btn.pack(side='right', padx=(10, 0))
        
        confirm_btn = ttk.Button(
            button_frame,
            text=confirm_text,
            command=self._on_confirm,
            style='Danger.TButton'
        )
        confirm_btn.pack(side='right')
        
        self.bind('<Escape>', lambda e: self._on_cancel())
        self.protocol('WM_DELETE_WINDOW', self._on_cancel)
    
    def _on_confirm(self):
        self.result = True
        self.destroy()
    
    def _on_cancel(self):
        self.result = False
        self.destroy()
    
    def show(self) -> bool:
        self.wait_window()
        return self.result
