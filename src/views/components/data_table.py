import tkinter as tk
from tkinter import ttk


class DataTable(tk.Frame):
    """Treeview tabanlı veri tablosu bileşeni"""
    
    def __init__(self, parent, columns: list, on_select=None, on_double_click=None, select_mode='browse'):
        """
        columns: [('id', 'ID', 50), ('name', 'Ad', 150), ...]
        select_mode: 'browse' (tek seçim) veya 'extended' (çoklu seçim)
        """
        super().__init__(parent)
        self.columns = columns
        self.on_select = on_select
        self.on_double_click = on_double_click
        self.select_mode = select_mode
        
        self._create_widgets()
    
    def _create_widgets(self):
        scrollbar_y = ttk.Scrollbar(self, orient='vertical')
        scrollbar_x = ttk.Scrollbar(self, orient='horizontal')
        
        column_ids = [col[0] for col in self.columns]
        self.tree = ttk.Treeview(
            self,
            columns=column_ids,
            show='headings',
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            selectmode=self.select_mode
        )
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        for col_id, col_text, col_width in self.columns:
            self.tree.heading(col_id, text=col_text, anchor='w')
            self.tree.column(col_id, width=col_width, minwidth=50)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)
    
    def load_data(self, data: list):
        self.clear()
        for row in data:
            values = [row.get(col[0], '') for col in self.columns]
            self.tree.insert('', 'end', values=values, tags=(str(row.get('id', '')),))
    
    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def get_selected(self) -> dict | None:
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return dict(zip([col[0] for col in self.columns], item['values']))
        return None
    
    def get_selected_id(self) -> int | None:
        selected = self.get_selected()
        return selected.get('id') if selected else None
    
    def get_selected_all(self) -> list:
        selection = self.tree.selection()
        results = []
        for item_id in selection:
            item = self.tree.item(item_id)
            row_data = dict(zip([col[0] for col in self.columns], item['values']))
            results.append(row_data)
        return results
    
    def get_selected_ids(self) -> list:
        selected_items = self.get_selected_all()
        return [item.get('id') for item in selected_items if item.get('id')]
    
    def get_selection_count(self) -> int:
        return len(self.tree.selection())
    
    def _on_select(self, event):
        if self.on_select:
            self.on_select(self.get_selected())
    
    def _on_double_click(self, event):
        if self.on_double_click:
            self.on_double_click(self.get_selected())
