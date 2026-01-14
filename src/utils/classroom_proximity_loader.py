"""
Derslik Yakınlık Yükleyici
Derslikler arası fiziksel yakınlık bilgilerini Excel/CSV dosyasından okur
ve Graph (Adjacency List) yapısında tutar.

"""

import os
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


@dataclass
class ClassroomNode:
    name: str
    block: str
    neighbors: Set[str]
    
    def add_neighbor(self, neighbor_name: str) -> None:
        self.neighbors.add(neighbor_name)
    
    def is_neighbor(self, other_name: str) -> bool:
        return other_name in self.neighbors


class ClassroomProximityLoader:
    
    DEFAULT_FILE_PATH = "exceller/Derslik Yakınlık (1).xlsx"
    
    DEFAULT_CSV_PATH = "exceller/Derslik Yakınlık (1).csv"
    
    def __init__(self, file_path: Optional[str] = None):

        self.file_path = file_path or self._resolve_default_path()
        self._classroom_graph: Dict[str, ClassroomNode] = {}
        self._block_classrooms: Dict[str, List[str]] = {}
        self._loaded = False
        
        self._load_data()
    
    def _resolve_default_path(self) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_dir, "..", self.DEFAULT_CSV_PATH)
        excel_path = os.path.join(base_dir, "..", self.DEFAULT_FILE_PATH)
        
        if os.path.exists(csv_path):
            return csv_path
        return excel_path
    
    def _load_data(self) -> None:
        if self._loaded:
            return
        
        try:
            self._load_from_excel()
        except ImportError:
            try:
                self._load_from_csv()
            except Exception:
                self._load_manual_data()
        except Exception:
            try:
                self._load_from_csv()
            except Exception:
                self._load_manual_data()
    
    def _load_from_excel(self) -> None:
        import pandas as pd
        
        file_path = self._get_actual_file_path()
        
        df = pd.read_excel(file_path, sheet_name="Sayfa1")
        
        self._parse_dataframe(df)
        self._loaded = True
    
    def _load_from_csv(self) -> None:
        import csv
        
        try:
            import pandas as pd
            file_path = self._get_actual_file_path()
            
            df = pd.read_excel(file_path, sheet_name="Sayfa1")
            csv_path = self._get_csv_path()
            df.to_csv(csv_path, index=False)
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self._parse_csv_reader(reader)
        except ImportError:
            csv_path = self._get_csv_path()
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self._parse_csv_reader(reader)
        except Exception:
            raise FileNotFoundError("CSV veya Excel dosyası bulunamadı")
        
        self._loaded = True
    
    def _parse_dataframe(self, df) -> None:
        for _, row in df.iterrows():
            block = str(row.get('BLOK', '')).strip()
            classroom = str(row.get('DERSLİK', '')).strip()
            nearby_str = str(row.get('YAKIN DERSLİK', '')).strip()
            
            if not classroom:
                continue
            
            self._add_classroom_data(block, classroom, nearby_str)
    
    def _parse_csv_reader(self, reader) -> None:
        for row in reader:
            block = row.get('BLOK', '').strip()
            classroom = row.get('DERSLİK', '').strip()
            nearby_str = row.get('YAKIN DERSLİK', '').strip()
            
            if not classroom:
                continue
            
            self._add_classroom_data(block, classroom, nearby_str)
    
    def _add_classroom_data(self, block: str, classroom: str, nearby_str: str) -> None:
        if classroom not in self._classroom_graph:
            node = ClassroomNode(name=classroom, block=block, neighbors=set())
            self._classroom_graph[classroom] = node
        else:
            node = self._classroom_graph[classroom]
            node.block = block  # Blok bilgisini güncelle
        
        if block not in self._block_classrooms:
            self._block_classrooms[block] = []
        if classroom not in self._block_classrooms[block]:
            self._block_classrooms[block].append(classroom)
        
        if nearby_str and nearby_str.lower() != 'nan':
            nearby_list = [n.strip() for n in nearby_str.split(',') if n.strip()]
            for nearby in nearby_list:
                node.add_neighbor(nearby)
                
                if nearby not in self._classroom_graph:
                    nearby_node = ClassroomNode(name=nearby, block='', neighbors=set())
                    self._block_classrooms.setdefault(block, []).append(nearby)
                    self._classroom_graph[nearby] = nearby_node
                self._classroom_graph[nearby].add_neighbor(classroom)
    
    def _load_manual_data(self) -> None:
        manual_data = [
            ("M", "M101", "S101,M201,M301,S201,S202"),
            ("M", "M201", "M301,M101,S201,S202"),
            ("M", "M301", "M201,M101,S201,S202"),
            ("S", "S101", "M101,S201,S202,M201,M301"),
            ("S", "S201", "S101,S202,M201,M301"),
            ("S", "S202", "S101,S201,M201,M301"),
            ("K", "K001", "K002,AMFİA,AMFİB"),
            ("K", "K002", "K001,AMFİA,AMFİB"),
            ("D", "D101", "D102,D103,D104,D201,D202"),
            ("D", "D102", "D101,D103,D104,D201,D202"),
            ("D", "D103", "D101,D102,D104,D201,D202"),
            ("D", "D201", "D202,D101,D103,D104,D102,D301,D302"),
            ("D", "D202", "D201,D101,D103,D104,D102,D301,D302"),
            ("D", "D301", "D201,D202,D302"),
            ("D", "D302", "D201,D202,D301"),
            ("D", "D401", "D301,D302,D403,D402"),
            ("D", "D402", "D301,D302,D403,D401"),
            ("D", "D403", "D301,D302,D402,D401"),
            ("E", "E101", "E102,D201,D202"),
            ("E", "E102", "E101,D201,D202"),
            ("A", "AMFİA", "AMFİB,K001,K002"),
            ("A", "AMFİB", "AMFİA,K001,K002"),
        ]
        
        for block, classroom, nearby_str in manual_data:
            self._add_classroom_data(block, classroom, nearby_str)
        
        self._loaded = True
    
    def _get_actual_file_path(self) -> str:
        """Gerçek dosya yolunu döndürür"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "..", self.DEFAULT_FILE_PATH)
    
    def _get_csv_path(self) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "..", self.DEFAULT_CSV_PATH)
    
    def get_neighbors(self, classroom_name: str) -> List[str]:
        if classroom_name in self._classroom_graph:
            return list(self._classroom_graph[classroom_name].neighbors)
        return []
    
    def are_neighbors(self, classroom1: str, classroom2: str) -> bool:
        neighbors = self.get_neighbors(classroom1)
        return classroom2 in neighbors
    
    def get_block(self, classroom_name: str) -> str:
        if classroom_name in self._classroom_graph:
            return self._classroom_graph[classroom_name].block
        return ""
    
    def get_classrooms_in_block(self, block: str) -> List[str]:
        return self._block_classrooms.get(block, [])
    
    def get_all_classrooms(self) -> List[str]:
        return list(self._classroom_graph.keys())
    
    def get_available_neighbors_for_combination(
        self, 
        classroom_name: str, 
        available_classrooms: List[str]
    ) -> List[str]:
        all_neighbors = self.get_neighbors(classroom_name)
        available_set = set(available_classrooms)
        
        available_neighbors = [n for n in all_neighbors if n in available_set]
        
        return available_neighbors
    
    def get_closest_classrooms(
        self, 
        classroom_name: str, 
        available_classrooms: List[str],
        limit: int = 5
    ) -> List[str]:
        available_set = set(available_classrooms)
        result = []
        
        direct_neighbors = self.get_neighbors(classroom_name)
        for neighbor in direct_neighbors:
            if neighbor in available_set and neighbor not in result:
                result.append(neighbor)
        
        block = self.get_block(classroom_name)
        if block:
            same_block = self.get_classrooms_in_block(block)
            for other in same_block:
                if other != classroom_name and other in available_set and other not in result:
                    result.append(other)
        
        for other in available_classrooms:
            if other != classroom_name and other not in result:
                result.append(other)
        
        return result[:limit]
    
    def reload(self) -> None:
        self._classroom_graph.clear()
        self._block_classrooms.clear()
        self._loaded = False
        self._load_data()
    
    def is_loaded(self) -> bool:
        return self._loaded
    
    def get_graph_stats(self) -> Dict:
        return {
            'total_classrooms': len(self._classroom_graph),
            'total_blocks': len(self._block_classrooms),
            'blocks': {block: len(classrooms) for block, classrooms in self._block_classrooms.items()},
            'classrooms': list(self._classroom_graph.keys())
        }


_instance: Optional[ClassroomProximityLoader] = None


def get_proximity_loader() -> ClassroomProximityLoader:
    global _instance
    if _instance is None:
        _instance = ClassroomProximityLoader()
    return _instance
