import tkinter as tk
from tkinter import messagebox

from src.views.components.data_table import DataTable
from src.controllers.dashboard_controller import DashboardController


class StudentScheduleView(tk.Toplevel):
    def __init__(self, parent, student_id, controller=None):
        super().__init__(parent)
        self.student_id = student_id
        self.controller = controller or DashboardController(self)

        self.title('Öğrenci Sınav Programı')
        self.geometry('900x600')
        self.minsize(700, 450)
        self.configure(bg='#ecf0f1')

        self._create_widgets()
        self._load_data()

    def _create_widgets(self):
        header_frame = tk.Frame(self, bg='#ecf0f1')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))

        title_label = tk.Label(
            header_frame,
            text='📅 Öğrenci Sınav Programı',
            font=('Segoe UI', 18, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        title_label.pack(side='left')

        table_frame = tk.Frame(self, bg='white', bd=1, relief='solid')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columns = [
            ('course_name', 'Ders Adı', 250),
            ('exam_date', 'Tarih', 120),
            ('exam_time', 'Saat', 120),
            ('classroom', 'Derslik', 180),
        ]

        self.data_table = DataTable(table_frame, columns=columns, select_mode='browse')
        self.data_table.pack(fill='both', expand=True)

    def _load_data(self):
        try:
            # TODO: implement in DashboardController: get_student_schedule(student_id: int | str) -> list[dict] | list
            schedule = self.controller.get_student_schedule(self.student_id)
        except AttributeError:
            messagebox.showerror('Hata', 'Öğrenci programı için controller yöntemi bulunamadı.')
            schedule = []
        except Exception as exc:
            messagebox.showerror('Hata', f'Öğrenci programı alınamadı: {str(exc)}')
            schedule = []

        data = []
        for item in schedule or []:
            if isinstance(item, dict):
                course_name = item.get('course_name') or item.get('name') or item.get('course') or '-'
                exam_date = item.get('exam_date') or item.get('date') or '-'
                time_value = item.get('time')
                start_time = item.get('start_time')
                end_time = item.get('end_time')
                classroom = item.get('classroom') or item.get('classroom_name') or '-'
            else:
                course_name = getattr(item, 'course_name', None) or getattr(item, 'name', None) or '-'
                exam_date = getattr(item, 'exam_date', None) or getattr(item, 'date', None) or '-'
                time_value = getattr(item, 'time', None)
                start_time = getattr(item, 'start_time', None)
                end_time = getattr(item, 'end_time', None)
                classroom = getattr(item, 'classroom', None) or getattr(item, 'classroom_name', None) or '-'

            if time_value:
                exam_time = str(time_value)
            elif start_time and end_time:
                exam_time = f'{start_time} - {end_time}'
            else:
                exam_time = '-'

            data.append({
                'course_name': course_name,
                'exam_date': str(exam_date),
                'exam_time': exam_time,
                'classroom': classroom,
            })

        self.data_table.load_data(data)
