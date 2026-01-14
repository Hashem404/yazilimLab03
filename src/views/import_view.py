import tkinter as tk
from tkinter import messagebox, filedialog


class ImportView(tk.Frame):
    title = '📥 Veri Yükleme'

    def __init__(self, parent, dashboard):
        super().__init__(parent, bg='#ecf0f1')
        self.dashboard = dashboard
        self.controller = dashboard.controller
        self.class_lists_folder = None
        self.proximity_file = None

        self._create_widgets()

    def _create_widgets(self):
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

        content_frame = tk.Frame(self, bg='#ecf0f1')
        content_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))

        class_list_frame = tk.LabelFrame(
            content_frame,
            text='Sınıf Listeleri',
            font=('Segoe UI', 10, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50',
            padx=15,
            pady=10
        )
        class_list_frame.pack(fill='x', pady=(0, 15))

        class_list_label = tk.Label(
            class_list_frame,
            text='Sınıf Listeleri Klasörünü Seç',
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        class_list_label.pack(anchor='w')

        class_list_btn = tk.Button(
            class_list_frame,
            text='Klasör Seç',
            font=('Segoe UI', 10),
            bg='#3498db',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._select_class_list_folder
        )
        class_list_btn.pack(anchor='w', pady=(8, 6))

        self.class_list_path_label = tk.Label(
            class_list_frame,
            text='Seçilmedi',
            font=('Segoe UI', 9),
            bg='#ecf0f1',
            fg='#7f8c8d'
        )
        self.class_list_path_label.pack(anchor='w')

        proximity_frame = tk.LabelFrame(
            content_frame,
            text='Derslik Yakınlığı',
            font=('Segoe UI', 10, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50',
            padx=15,
            pady=10
        )
        proximity_frame.pack(fill='x', pady=(0, 15))

        proximity_label = tk.Label(
            proximity_frame,
            text='Derslik Yakınlık Dosyasını Seç',
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        proximity_label.pack(anchor='w')

        proximity_btn = tk.Button(
            proximity_frame,
            text='Dosya Seç',
            font=('Segoe UI', 10),
            bg='#16a085',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._select_proximity_file
        )
        proximity_btn.pack(anchor='w', pady=(8, 6))

        self.proximity_path_label = tk.Label(
            proximity_frame,
            text='Seçilmedi',
            font=('Segoe UI', 9),
            bg='#ecf0f1',
            fg='#7f8c8d'
        )
        self.proximity_path_label.pack(anchor='w')

        action_frame = tk.Frame(content_frame, bg='#ecf0f1')
        action_frame.pack(fill='x', pady=(10, 0))

        upload_btn = tk.Button(
            action_frame,
            text='Yükle ve Kaydet',
            font=('Segoe UI', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self._on_upload
        )
        upload_btn.pack(anchor='e')

    def _select_class_list_folder(self):
        folder_path = filedialog.askdirectory(title='Sınıf Listeleri Klasörü Seç')
        if folder_path:
            self.class_lists_folder = folder_path
            self.class_list_path_label.config(text=folder_path)

    def _select_proximity_file(self):
        file_path = filedialog.askopenfilename(
            title='Derslik Yakınlık Dosyası Seç',
            filetypes=[
                ('CSV Dosyaları', '*.csv'),
                ('Tüm Dosyalar', '*.*')
            ]
        )
        if file_path:
            self.proximity_file = file_path
            self.proximity_path_label.config(text=file_path)

    def _on_upload(self):
        if not self.class_lists_folder:
            messagebox.showwarning('Uyarı', 'Lütfen sınıf listeleri klasörünü seçin.')
            return
        if not self.proximity_file:
            messagebox.showwarning('Uyarı', 'Lütfen derslik yakınlık dosyasını seçin.')
            return

        try:
            # TODO: implement in DashboardController: import_class_lists_folder(folder_path: str) -> dict/None
            class_list_result = self.controller.import_class_lists_folder(self.class_lists_folder)
        except AttributeError:
            messagebox.showerror('Hata', 'Sınıf listeleri yükleme yöntemi bulunamadı.')
            return
        except Exception as exc:
            messagebox.showerror('Hata', f'Sınıf listeleri yüklenemedi: {str(exc)}')
            return

        try:
            # TODO: implement in DashboardController: import_classroom_proximity(filepath: str) -> dict/None
            proximity_result = self.controller.import_classroom_proximity(self.proximity_file)
        except AttributeError:
            messagebox.showerror('Hata', 'Yakınlık yükleme yöntemi bulunamadı.')
            return
        except Exception as exc:
            messagebox.showerror('Hata', f'Yakınlık dosyası yüklenemedi: {str(exc)}')
            return

        if isinstance(class_list_result, dict) and not class_list_result.get('success', True):
            messagebox.showerror('Hata', class_list_result.get('message', 'Sınıf listeleri yüklenemedi.'))
            return
        if isinstance(proximity_result, dict) and not proximity_result.get('success', True):
            messagebox.showerror('Hata', proximity_result.get('message', 'Yakınlık dosyası yüklenemedi.'))
            return

        messagebox.showinfo('Başarılı', 'Veriler başarıyla yüklendi.')
