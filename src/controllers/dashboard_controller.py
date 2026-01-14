"""
Dashboard controller - Ana panel kontrolü
View ile Service arasında köprü görevi görür
"""

from typing import List, Dict, Any, Optional
from datetime import date, timedelta
from src.services.faculty_service import FacultyService
from src.services.department_service import DepartmentService
from src.services.classroom_service import ClassroomService
from src.services.lecturer_service import LecturerService
from src.services.course_service import CourseService
from src.services.exam_schedule_service import ExamScheduleService
from src.services.scheduler_service import SchedulerService
from src.services.student_import_service import StudentImportService
from src.utils.classroom_proximity_loader import ClassroomProximityLoader


class DashboardController:
    
    def __init__(self, view: Any = None):
        self.view = view
        self.faculty_service = FacultyService()
        self.department_service = DepartmentService()
        self.classroom_service = ClassroomService()
        self.lecturer_service = LecturerService()
        self.course_service = CourseService()
        self.exam_service = ExamScheduleService()
        self.scheduler_service = SchedulerService()
        self.student_import_service = StudentImportService()
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        stats = {
            'total_faculties': self.faculty_service.get_count(),
            'total_departments': self.department_service.get_count(),
            'total_classrooms': self.classroom_service.get_count(),
            'total_lecturers': self.lecturer_service.get_count(),
            'total_courses': self.course_service.get_count(),
            'total_exams': self.exam_service.get_count()
        }
        
        today = date.today()
        week_end = today + timedelta(days=7)
        week_exams = self.exam_service.get_by_date_range(today, week_end)
        stats['this_week_exams'] = len([e for e in week_exams if e.exam_date >= today])
        
        stats['pending_exams'] = len(self.exam_service.get_by_status('planned'))
        
        today_exams = self.exam_service.get_by_date(today)
        stats['today_exams'] = len(today_exams)
        
        return stats
    
    def get_recent_exams(self, limit: int = 10) -> List[Dict]:
        exams = self.exam_service.get_all()
        exams.sort(key=lambda e: (e.exam_date, e.start_time), reverse=True)
        
        result = []
        for exam in exams[:limit]:
            result.append({
                'date': exam.exam_date,
                'time': str(exam.start_time),
                'start_time': str(exam.start_time),
                'end_time': str(exam.end_time) if exam.end_time else '',
                'course_code': exam.course_code,
                'course_name': exam.course_name,
                'lecturer': exam.lecturer_name,
                'lecturer_name': exam.lecturer_name,
                'classroom': f"{exam.faculty_name or 'Belirsiz'} - {exam.classroom_name}",
                'classroom_name': exam.classroom_name,
                'faculty_name': exam.faculty_name or 'Belirsiz',
                'student_count': exam.student_count,
                'exam_type': exam.exam_type,
                'status': exam.status
            })
        
        return result
    
    def get_upcoming_exams(self, days: int = 7) -> List[Dict]:
        today = date.today()
        end_date = today + timedelta(days=days)
        exams = self.exam_service.get_by_date_range(today, end_date)
        
        upcoming = [e for e in exams if e.exam_date >= today]
        upcoming.sort(key=lambda e: (e.exam_date, e.start_time))
        
        result = []
        for exam in upcoming:
            result.append({
                'date': exam.exam_date,
                'time': str(exam.start_time),
                'start_time': str(exam.start_time),
                'end_time': str(exam.end_time) if exam.end_time else '',
                'course_code': exam.course_code,
                'course_name': exam.course_name,
                'lecturer': exam.lecturer_name,
                'lecturer_name': exam.lecturer_name,
                'classroom': f"{exam.faculty_name or 'Belirsiz'} - {exam.classroom_name}",
                'classroom_name': exam.classroom_name,
                'faculty_name': exam.faculty_name or 'Belirsiz',
                'student_count': exam.student_count,
                'exam_type': exam.exam_type,
                'status': exam.status
            })
        
        return result
    
    def get_exam_schedule_by_date(self, target_date: date) -> List[Dict]:
        exams = self.exam_service.get_by_date(target_date)
        
        result = []
        for exam in exams:
            result.append({
                'time': f"{exam.start_time} - {exam.end_time}",
                'course_code': exam.course_code,
                'course_name': exam.course_name,
                'lecturer': exam.lecturer_name,
                'classroom': f"{exam.faculty_name or 'Belirsiz'} - {exam.classroom_name}",
                'student_count': exam.student_count,
                'status': exam.status
            })
        
        return result
    
    def get_faculty_distribution(self) -> List[Dict]:
        """Fakülte dağılımını döndürür"""
        faculties = self.faculty_service.get_all()
        
        result = []
        for faculty in faculties:
            departments = self.department_service.get_by_faculty_id(faculty.id)
            result.append({
                'faculty_name': faculty.name,
                'department_count': len(departments),
                'code': faculty.code
            })
        
        return result
    
    def get_classroom_utilization(self, exam_date: date) -> Dict[str, Any]:
        all_classrooms = self.classroom_service.get_all()
        scheduled_exams = self.exam_service.get_by_date(exam_date)
        
        time_slots = [
            ("09:00-10:30", "09:00", "10:30"),
            ("11:00-12:30", "11:00", "12:30"),
            ("13:30-15:00", "13:30", "15:00"),
            ("15:30-17:00", "15:30", "17:00")
        ]
        
        utilization = {}
        total_capacity = sum(c.capacity for c in all_classrooms)
        
        for slot_name, start, end in time_slots:
            slot_exams = [
                e for e in scheduled_exams
                if str(e.start_time) <= start and str(e.end_time) >= end
            ]
            
            if slot_exams:
                used_classrooms = set(e.classroom_id for e in slot_exams)
                used_capacity = sum(
                    self.classroom_service.get_by_id(c_id).capacity
                    for c_id in used_classrooms
                    if self.classroom_service.get_by_id(c_id)
                )
                
                utilization[slot_name] = {
                    'used_classrooms': len(used_classrooms),
                    'total_classrooms': len(all_classrooms),
                    'used_capacity': used_capacity,
                    'total_capacity': total_capacity,
                    'percentage': (used_capacity / total_capacity * 100) if total_capacity > 0 else 0
                }
            else:
                utilization[slot_name] = {
                    'used_classrooms': 0,
                    'total_classrooms': len(all_classrooms),
                    'used_capacity': 0,
                    'total_capacity': total_capacity,
                    'percentage': 0
                }
        
        return utilization
    
    def generate_auto_schedule(self, start_date: date, end_date: date,
                              department_id: int = None, exam_type: str = "final") -> Dict:
 
        start_date_str = start_date.strftime('%Y-%m-%d') if isinstance(start_date, date) else str(start_date)
        end_date_str = end_date.strftime('%Y-%m-%d') if isinstance(end_date, date) else str(end_date)
        
        result = self.scheduler_service.generate_schedule(
            start_date_str, end_date_str, department_id, exam_type
        )
        
        if isinstance(result, dict):
            return result
        return {'success': False, 'message': 'Beklenmeyen hata', 'failed_courses': []}
    
    def get_schedule_conflicts(self, start_date: date, end_date: date) -> List[Dict]:
        conflicts = []
        
        exams = self.exam_service.get_by_date_range(start_date, end_date)
        
        for i, exam1 in enumerate(exams):
            for exam2 in exams[i+1:]:
                if (exam1.exam_date == exam2.exam_date and
                    exam1.classroom_id == exam2.classroom_id and
                    exam1.status != 'cancelled' and exam2.status != 'cancelled'):
                    
                    if (exam1.start_time < exam2.end_time and
                        exam1.end_time > exam2.start_time):
                        
                        conflicts.append({
                            'type': 'classroom_conflict',
                            'date': str(exam1.exam_date),
                            'time': f"{exam1.start_time}-{exam1.end_time}",
                            'classroom': exam1.classroom_name,
                            'course1': exam1.course_code,
                            'course2': exam2.course_code
                        })
        
        return conflicts
    
    # ==================== FAKÜLTE İŞLEMLERİ ====================
    
    def get_all_faculties(self) -> list:
        return self.faculty_service.get_all()
    
    def create_faculty(self, data: dict) -> dict:
        try:
            success, message, faculty_id = self.faculty_service.create(
                name=data.get('name', ''),
                code=data.get('code', ''),
                dean_name=data.get('dean_name')
            )
            return {
                'success': success,
                'data': faculty_id,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'data': None, 'message': str(e)}
    
    def update_faculty(self, id: int, data: dict) -> dict:
        try:
            success, message = self.faculty_service.update(
                faculty_id=id,
                name=data.get('name', ''),
                code=data.get('code', ''),
                dean_name=data.get('dean_name')
            )
            return {
                'success': success,
                'data': None,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'data': None, 'message': str(e)}
    
    def delete_faculty(self, id: int) -> dict:
        try:
            success, message = self.faculty_service.delete(id)
            return {
                'success': success,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    # ==================== BÖLÜM İŞLEMLERİ ====================
    
    def get_all_departments(self) -> list:
        return self.department_service.get_all()
    
    def get_departments_by_faculty(self, faculty_id: int) -> list:
        return self.department_service.get_by_faculty_id(faculty_id)
    
    def create_department(self, data: dict) -> dict:
        try:
            success, message, department_id = self.department_service.create(
                faculty_id=data.get('faculty_id'),
                name=data.get('name', ''),
                code=data.get('code', ''),
                head_name=data.get('head_name')
            )
            return {
                'success': success,
                'data': department_id,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'data': None, 'message': str(e)}
    
    def update_department(self, id: int, data: dict) -> dict:
        try:
            success, message = self.department_service.update(
                department_id=id,
                faculty_id=data.get('faculty_id'),
                name=data.get('name', ''),
                code=data.get('code', ''),
                head_name=data.get('head_name')
            )
            return {
                'success': success,
                'data': None,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'data': None, 'message': str(e)}
    
    def delete_department(self, id: int) -> dict:
        try:
            success, message = self.department_service.delete(id)
            return {
                'success': success,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    # ==================== DERSLİK İŞLEMLERİ ====================
    
    def get_all_classrooms(self) -> list:
        return self.classroom_service.get_all()
    
    def get_classrooms_by_faculty(self, faculty_id: int) -> list:
        return self.classroom_service.get_by_faculty(faculty_id)
    
    def create_classroom(self, data: dict) -> dict:
        try:
            success, message, classroom_id = self.classroom_service.create(
                name=data.get('name', ''),
                faculty_id=int(data.get('faculty_id', 0)),
                capacity=int(data.get('capacity', 0)),
                has_computer=bool(data.get('has_computer', False)),
                is_suitable=bool(data.get('is_suitable', True))
            )
            return {
                'success': success,
                'data': classroom_id,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'data': None, 'message': str(e)}
    
    def update_classroom(self, id: int, data: dict) -> dict:
        try:
            success, message = self.classroom_service.update(
                classroom_id=id,
                name=data.get('name', ''),
                faculty_id=int(data.get('faculty_id', 0)),
                capacity=int(data.get('capacity', 0)),
                has_computer=bool(data.get('has_computer', False)),
                is_suitable=bool(data.get('is_suitable', True))
            )
            return {
                'success': success,
                'data': None,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'data': None, 'message': str(e)}
    
    def delete_classroom(self, id: int) -> dict:
        try:
            success, message = self.classroom_service.delete(id)
            return {
                'success': success,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_exam_suitable_classrooms(self) -> list:
        return self.classroom_service.get_exam_suitable()
    
    # ==================== ÖĞRETİM ÜYESİ İŞLEMLERİ ====================
    
    def get_all_lecturers(self) -> list:
        return self.lecturer_service.get_all()
    
    def get_lecturers_by_department(self, department_id: int) -> list:
        return self.lecturer_service.get_by_department_id(department_id)
    
    def create_lecturer(self, data: dict) -> dict:
        try:
            success, message, lecturer_id = self.lecturer_service.create(
                department_id=data.get('department_id'),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                title=data.get('title', ''),
                email=data.get('email'),
                available_days=data.get('available_days')
            )
            return {
                'success': success,
                'data': lecturer_id,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'data': None, 'message': str(e)}
    
    def update_lecturer(self, id: int, data: dict) -> dict:
        try:
            success, message = self.lecturer_service.update(
                lecturer_id=id,
                department_id=data.get('department_id'),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                title=data.get('title', ''),
                email=data.get('email'),
                available_days=data.get('available_days')
            )
            return {
                'success': success,
                'data': None,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'data': None, 'message': str(e)}
    
    def delete_lecturer(self, id: int) -> dict:
        try:
            success, message = self.lecturer_service.delete(id)
            return {
                'success': success,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    # ==================== DERS İŞLEMLERİ ====================
    
    def get_all_courses(self) -> list:
        return self.course_service.get_all()
    
    def get_courses_by_department(self, department_id: int) -> list:
        return self.course_service.get_by_department_id(department_id)
    
    def create_course(self, data: dict) -> dict:
        try:
            success, message, course_id = self.course_service.create(
                department_id=data.get('department_id'),
                lecturer_id=data.get('lecturer_id'),
                code=data.get('code', ''),
                name=data.get('name', ''),
                credit=int(data.get('credit', 3)),
                year=int(data.get('year', 1)),
                semester=int(data.get('semester', 1)),
                student_count=int(data.get('student_count', 0)),
                lecturer_count=int(data.get('lecturer_count', 1)),
                exam_type=data.get('exam_type', 'Yazılı'),
                exam_duration=int(data.get('exam_duration', 60)),
                has_exam=bool(data.get('has_exam', True)),
                period=int(data.get('period', 1)) if data.get('period') else None,
                theory_hours=int(data.get('theory_hours', 0)),
                lab_hours=int(data.get('lab_hours', 0)),
                course_type=data.get('course_type', 'Zorunlu'),
                description=data.get('description', '')
            )
            return {
                'success': success,
                'data': course_id,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'data': None, 'message': str(e)}
    
    def update_course(self, id: int, data: dict) -> dict:
        try:
            success, message = self.course_service.update(
                course_id=id,
                department_id=data.get('department_id'),
                lecturer_id=data.get('lecturer_id'),
                code=data.get('code', ''),
                name=data.get('name', ''),
                credit=int(data.get('credit', 3)),
                year=int(data.get('year', 1)),
                semester=int(data.get('semester', 1)),
                student_count=int(data.get('student_count', 0)),
                lecturer_count=int(data.get('lecturer_count', 1)),
                exam_type=data.get('exam_type', 'Yazılı'),
                exam_duration=int(data.get('exam_duration', 60)),
                has_exam=bool(data.get('has_exam', True)),
                period=int(data.get('period', 1)) if data.get('period') else None,
                theory_hours=int(data.get('theory_hours', 0)),
                lab_hours=int(data.get('lab_hours', 0)),
                course_type=data.get('course_type', 'Zorunlu'),
                description=data.get('description', '')
            )
            return {
                'success': success,
                'data': None,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'data': None, 'message': str(e)}
    
    def delete_course(self, id: int) -> dict:
        try:
            success, message = self.course_service.delete(id)
            return {
                'success': success,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    # ==================== SINAV PROGRAMI İŞLEMLERİ ====================
    
    def get_all_exams(self) -> list:
        return self.exam_service.get_all()
    
    def get_exams_by_date(self, exam_date: str) -> list:
        if isinstance(exam_date, str):
            exam_date = date.fromisoformat(exam_date)
        return self.exam_service.get_by_date(exam_date)
    
    def create_exam(self, data: dict) -> dict:
        try:
            from datetime import time as dt_time
            
            exam_date = data.get('exam_date')
            if isinstance(exam_date, str):
                exam_date = date.fromisoformat(exam_date)
            
            start_time = data.get('start_time')
            if isinstance(start_time, str):
                parts = start_time.split(':')
                start_time = dt_time(int(parts[0]), int(parts[1]))
            
            end_time = data.get('end_time')
            if isinstance(end_time, str):
                parts = end_time.split(':')
                end_time = dt_time(int(parts[0]), int(parts[1]))
            
            classroom_ids = data.get('classroom_ids', [])
            
            if not classroom_ids and data.get('classroom_id'):
                classroom_ids = [data.get('classroom_id')]
            
            if len(classroom_ids) > 1:
                success, message, schedule_id = self.exam_service.create_multi_classroom(
                    course_id=data.get('course_id'),
                    classroom_ids=classroom_ids,
                    exam_date=exam_date,
                    start_time=start_time,
                    end_time=end_time,
                    exam_type=data.get('exam_type', 'final'),
                    notes=data.get('notes')
                )
            else:
                classroom_id = classroom_ids[0] if classroom_ids else data.get('classroom_id')
                success, message, schedule_id = self.exam_service.create(
                    course_id=data.get('course_id'),
                    classroom_id=classroom_id,
                    exam_date=exam_date,
                    start_time=start_time,
                    end_time=end_time,
                    exam_type=data.get('exam_type', 'final'),
                    notes=data.get('notes')
                )
            
            return {
                'success': success,
                'data': schedule_id,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'data': None, 'message': str(e)}
    
    def update_exam(self, id: int, data: dict) -> dict:
        try:
            from datetime import time as dt_time
            
            exam_date = data.get('exam_date')
            if isinstance(exam_date, str):
                exam_date = date.fromisoformat(exam_date)
            
            start_time = data.get('start_time')
            if isinstance(start_time, str):
                parts = start_time.split(':')
                start_time = dt_time(int(parts[0]), int(parts[1]))
            
            end_time = data.get('end_time')
            if isinstance(end_time, str):
                parts = end_time.split(':')
                end_time = dt_time(int(parts[0]), int(parts[1]))
            
            success, message = self.exam_service.update(
                schedule_id=id,
                course_id=data.get('course_id'),
                classroom_id=data.get('classroom_id'),
                exam_date=exam_date,
                start_time=start_time,
                end_time=end_time,
                exam_type=data.get('exam_type', 'final'),
                status=data.get('status', 'planned'),
                notes=data.get('notes')
            )
            return {
                'success': success,
                'data': None,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'data': None, 'message': str(e)}
    
    def delete_exam(self, id: int) -> dict:
        try:
            success, message = self.exam_service.delete(id)
            return {
                'success': success,
                'message': message
            }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    # ==================== OTOMATİK PLANLAMA İŞLEMLERİ ====================
    
    def generate_schedule(self, start_date: str, end_date: str) -> dict:
        try:
            if isinstance(start_date, str):
                start_date = date.fromisoformat(start_date)
            if isinstance(end_date, str):
                end_date = date.fromisoformat(end_date)
            
            success, message = self.scheduler_service.generate_schedule(
                start_date, end_date
            )
            return {
                'success': success,
                'message': message,
                'data': None
            }
        except Exception as e:
            return {'success': False, 'message': str(e), 'data': None}
    
    def get_schedule_statistics(self) -> dict:
        try:
            return self.scheduler_service.get_schedule_statistics()
        except Exception as e:
            return {'error': str(e)}
    
    # ==================== FAKÜLTE/BÖLÜM BAZLI SINAV RAPORLARI ====================
    
    def get_exams_by_faculty(self, faculty_id: int) -> List[Dict]:
        exams = self.exam_service.get_by_faculty_id(faculty_id)
        
        result = []
        for exam in exams:
            result.append({
                'date': exam.exam_date,
                'time': str(exam.start_time),
                'start_time': str(exam.start_time),
                'end_time': str(exam.end_time) if exam.end_time else '',
                'course_code': exam.course_code,
                'course_name': exam.course_name,
                'lecturer': exam.lecturer_name,
                'lecturer_name': exam.lecturer_name,
                'classroom': exam.classroom_name,
                'classroom_name': exam.classroom_name,
                'faculty_name': exam.faculty_name or 'Belirsiz',
                'department_name': exam.department_name or 'Belirsiz',
                'student_count': exam.student_count,
                'exam_type': exam.exam_type,
                'status': exam.status
            })
        
        return result
    
    def get_exams_by_department(self, department_id: int) -> List[Dict]:
        exams = self.exam_service.get_by_department_id(department_id)
        
        result = []
        for exam in exams:
            result.append({
                'date': exam.exam_date,
                'time': str(exam.start_time),
                'start_time': str(exam.start_time),
                'end_time': str(exam.end_time) if exam.end_time else '',
                'course_code': exam.course_code,
                'course_name': exam.course_name,
                'lecturer': exam.lecturer_name,
                'lecturer_name': exam.lecturer_name,
                'classroom': exam.classroom_name,
                'classroom_name': exam.classroom_name,
                'faculty_name': exam.faculty_name or 'Belirsiz',
                'department_name': exam.department_name or 'Belirsiz',
                'student_count': exam.student_count,
                'exam_type': exam.exam_type,
                'status': exam.status
            })
        
        return result
    
    def get_exams_by_faculty_or_department(self, faculty_id: int = None, department_id: int = None) -> List[Dict]:
        if department_id:
            return self.get_exams_by_department(department_id)
        elif faculty_id:
            return self.get_exams_by_faculty(faculty_id)
        else:
            return self.get_upcoming_exams(days=365)
    
    # ==================== KULLANICI BAZLI FİLTRELEME ====================
    
    def filter_schedule_by_user(self, user_info: dict) -> List[Dict]:
        """
        Kullanıcı rolüne göre sınav programını filtreler.
        
        - Hoca (lecturer): Kendi verdiği derslerin sınavlarını görür
        - Öğrenci (ogrenci): Aldığı derslerin sınavlarını görür
        
        Args:
            user_info: {'id', 'username', 'role', 'department_id', 'student_number', 'lecturer_id'}
            
        Returns:
            List[Dict]: Filtrelenmiş sınav listesi
        """
        if not user_info:
            return []
        
        role = user_info.get('role', '').lower()
        
        # Hoca ise kendi derslerinin sınavlarını göster
        if role in ('hoca', 'lecturer'):
            lecturer_id = user_info.get('lecturer_id')
            if lecturer_id:
                return self._get_exams_for_lecturer(lecturer_id)
            # lecturer_id yoksa bölüm bazlı fallback
            department_id = user_info.get('department_id')
            if department_id:
                return self.get_exams_by_department(department_id)
        
        # Öğrenci ise aldığı derslerin sınavlarını göster
        elif role in ('ogrenci', 'student'):
            student_id = user_info.get('student_id')
            student_number = user_info.get('student_number')
            
            if student_id:
                return self._get_exams_for_student(student_id)
            elif student_number:
                return self._get_exams_for_student_number(student_number)
            # Hiçbiri yoksa bölüm bazlı fallback
            department_id = user_info.get('department_id')
            if department_id:
                return self.get_exams_by_department(department_id)
        
        # Admin ve Bölüm Yetkilisi için tüm sınavları döndür
        return self.get_upcoming_exams(days=365)
    
    def _get_exams_for_lecturer(self, lecturer_id: int) -> List[Dict]:
        """
        Belirli bir öğretim üyesinin derslerinin sınavlarını döndürür.
        """
        exams = self.exam_service.get_by_lecturer_all(lecturer_id)
        
        result = []
        for exam in exams:
            result.append({
                'id': exam.id,
                'date': exam.exam_date,
                'time': str(exam.start_time),
                'start_time': str(exam.start_time),
                'end_time': str(exam.end_time) if exam.end_time else '',
                'course_id': exam.course_id,
                'course_code': exam.course_code,
                'course_name': exam.course_name,
                'lecturer': exam.lecturer_name,
                'lecturer_name': exam.lecturer_name,
                'classroom': exam.classroom_name,
                'classroom_name': exam.classroom_name,
                'faculty_name': exam.faculty_name or 'Belirsiz',
                'department_name': exam.department_name or 'Belirsiz',
                'student_count': exam.student_count,
                'exam_type': exam.exam_type,
                'status': exam.status
            })
        
        return result
    
    def _get_exams_for_student(self, student_id: int) -> List[Dict]:
        """
        Belirli bir öğrencinin aldığı derslerin sınavlarını döndürür.
        """
        exams = self.exam_service.get_by_student_id(student_id)
        
        result = []
        for exam in exams:
            result.append({
                'id': exam.id,
                'date': exam.exam_date,
                'time': str(exam.start_time),
                'start_time': str(exam.start_time),
                'end_time': str(exam.end_time) if exam.end_time else '',
                'course_id': exam.course_id,
                'course_code': exam.course_code,
                'course_name': exam.course_name,
                'lecturer': exam.lecturer_name,
                'lecturer_name': exam.lecturer_name,
                'classroom': exam.classroom_name,
                'classroom_name': exam.classroom_name,
                'faculty_name': exam.faculty_name or 'Belirsiz',
                'department_name': exam.department_name or 'Belirsiz',
                'student_count': exam.student_count,
                'exam_type': exam.exam_type,
                'status': exam.status
            })
        
        return result
    
    def _get_exams_for_student_number(self, student_number: str) -> List[Dict]:
        """
        Öğrenci numarasına göre sınavları döndürür.
        """
        exams = self.exam_service.get_by_student_number(student_number)
        
        result = []
        for exam in exams:
            result.append({
                'id': exam.id,
                'date': exam.exam_date,
                'time': str(exam.start_time),
                'start_time': str(exam.start_time),
                'end_time': str(exam.end_time) if exam.end_time else '',
                'course_id': exam.course_id,
                'course_code': exam.course_code,
                'course_name': exam.course_name,
                'lecturer': exam.lecturer_name,
                'lecturer_name': exam.lecturer_name,
                'classroom': exam.classroom_name,
                'classroom_name': exam.classroom_name,
                'faculty_name': exam.faculty_name or 'Belirsiz',
                'department_name': exam.department_name or 'Belirsiz',
                'student_count': exam.student_count,
                'exam_type': exam.exam_type,
                'status': exam.status
            })
        
        return result
    
    # ==================== VERİ İTHAL İŞLEMLERİ ====================
    
    def import_class_lists_folder(self, folder_path: str, semester: str = None) -> Dict:
        """
        Sınıf listeleri klasöründen Excel dosyalarını içe aktarır.
        
        Args:
            folder_path: Excel dosyalarının bulunduğu klasör yolu
            semester: Dönem bilgisi (opsiyonel)
            
        Returns:
            Dict: {'success': bool, 'message': str, 'summary': dict}
        """
        try:
            results = self.student_import_service.import_from_excel_directory(
                directory_path=folder_path,
                semester=semester
            )
            
            summary = self.student_import_service.get_import_summary(results)
            
            return {
                'success': True,
                'message': f"{summary['successful_files']}/{summary['total_files']} dosya başarıyla içe aktarıldı. {summary['total_students_imported']} öğrenci eklendi.",
                'summary': summary,
                'details': results
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Sınıf listeleri yüklenemedi: {str(e)}"
            }
    
    def import_classroom_proximity(self, file_path: str) -> Dict:
        """
        Derslik yakınlık dosyasını yükler.
        
        Args:
            file_path: CSV veya Excel dosyasının yolu
            
        Returns:
            Dict: {'success': bool, 'message': str, 'stats': dict}
        """
        try:
            loader = ClassroomProximityLoader(file_path)
            stats = loader.get_graph_stats()
            
            return {
                'success': True,
                'message': f"Derslik yakınlık verisi başarıyla yüklendi. {stats['total_classrooms']} derslik, {stats['total_blocks']} blok.",
                'stats': stats
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Derslik yakınlık dosyası yüklenemedi: {str(e)}"
            }
    
    def get_classroom_proximity_stats(self) -> Dict:
        """
        Mevcut derslik yakınlık verisi istatistiklerini döndürür.
        
        Returns:
            Dict: {'total_classrooms': int, 'total_blocks': int, 'blocks': dict, 'classrooms': list}
        """
        try:
            loader = ClassroomProximityLoader()
            return loader.get_graph_stats()
        except Exception as e:
            return {
                'error': str(e),
                'total_classrooms': 0,
                'total_blocks': 0,
                'blocks': {},
                'classrooms': []
            }
