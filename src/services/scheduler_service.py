"""
Sınav planlama algoritması servisi
Greedy + Backtracking yaklaşımı ile otomatik sınav programı oluşturma

"""

from typing import List, Dict, Tuple, Optional, Set
from datetime import date, time, timedelta, datetime
from dataclasses import dataclass

from src.models.course import Course
from src.models.classroom import Classroom
from src.models.exam_schedule import ExamSchedule
from src.models.lecturer import Lecturer, DEFAULT_AVAILABLE_DAYS
from src.repositories.course_repository import CourseRepository
from src.repositories.classroom_repository import ClassroomRepository
from src.repositories.exam_schedule_repository import ExamScheduleRepository
from src.repositories.lecturer_repository import LecturerRepository
from src.repositories.department_repository import DepartmentRepository
from src.repositories.student_repository import StudentCourseRepository
from src.utils.classroom_proximity_loader import get_proximity_loader


@dataclass
class TimeSlot:
    start_time: time
    end_time: time
    base_slot: bool = True
    
    def overlaps(self, other: 'TimeSlot') -> bool:
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)
    
    def duration_minutes(self) -> int:
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        return end_minutes - start_minutes
    
    def fits_duration(self, duration: int) -> bool:
        return self.duration_minutes() >= duration
    
    def can_combine_with(self, other: 'TimeSlot', break_minutes: int = 30) -> bool:
        """Bu slot ile diğer slot birleştirilebilir mi?
        
        İki slot arasındaki boşluk belirli bir süreden kısa ise birleştirilebilir.
        Örn: 09:00-11:00 ve 11:30-13:30 arası 30 dakika ara var -> birleştirilebilir
        """
        if self.end_time > other.start_time:
            return False
        
        gap_minutes = (other.start_time.hour * 60 + other.start_time.minute) - \
                      (self.end_time.hour * 60 + self.end_time.minute)
        return gap_minutes <= break_minutes
    
    @staticmethod
    def combine_slots(slot1: 'TimeSlot', slot2: 'TimeSlot') -> 'TimeSlot':
        """İki slotu birleştirir ve yeni bir slot döndürür"""
        return TimeSlot(
            start_time=slot1.start_time,
            end_time=slot2.end_time,
            base_slot=False  # Birleştirilmiş slot
        )


@dataclass
class ScheduleSlot:
    exam_date: date
    time_slot: TimeSlot
    classroom: Classroom
    is_available: bool = True


class SchedulerService:
    DEFAULT_TIME_SLOTS = [
        TimeSlot(time(9, 0), time(11, 0)),    # 09:00 - 11:00 (120 dk)
        TimeSlot(time(11, 30), time(13, 30)), # 11:30 - 13:30 (120 dk)
        TimeSlot(time(14, 0), time(16, 0)),   # 14:00 - 16:00 (120 dk)
        TimeSlot(time(16, 30), time(18, 30)), # 16:30 - 18:30 (120 dk)
    ]
    
    WEEKDAYS = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']
    
    TURKISH_CHAR_MAP = {
        'ı': 'i', 'İ': 'I',
        'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'Ü': 'U',
        'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O',
        'ç': 'c', 'Ç': 'C'
    }
    
    DAY_ALIASES = {
        'pazartesi': 'Pazartesi',
        'sali': 'Salı',
        'salı': 'Salı',
        'carsamba': 'Çarşamba',
        'çarsamba': 'Çarşamba',
        'çarşamba': 'Çarşamba',
        'persembe': 'Perşembe',
        'perşembe': 'Perşembe',
        'cuma': 'Cuma'
    }
    
    def __init__(self, use_student_based_conflict: bool = True):
        self.course_repo = CourseRepository()
        self.classroom_repo = ClassroomRepository()
        self.exam_repo = ExamScheduleRepository()
        self.lecturer_repo = LecturerRepository()
        self.department_repo = DepartmentRepository()
        self.student_course_repo = StudentCourseRepository()
        
        self.time_slots = self.DEFAULT_TIME_SLOTS
        
        self.proximity_loader = get_proximity_loader()
        
        self.use_student_based_conflict = use_student_based_conflict
        
        self._course_student_cache: Dict[int, Set[int]] = {}
    
    def get_time_slots_for_duration(self, exam_duration: int) -> List[TimeSlot]:

        suitable_standard = [slot for slot in self.DEFAULT_TIME_SLOTS
                            if slot.fits_duration(exam_duration)]
        if suitable_standard:
            return suitable_standard
        
        return self._generate_combined_slots(exam_duration)
    
    def _generate_combined_slots(self, required_duration: int) -> List[TimeSlot]:

        combined_slots = []
        
        max_standard_duration = sum(slot.duration_minutes() for slot in self.DEFAULT_TIME_SLOTS)
        
        if required_duration > max_standard_duration:
            first_slot_start = self.DEFAULT_TIME_SLOTS[0].start_time
            ultra_end_minutes = (first_slot_start.hour * 60 + first_slot_start.minute) + required_duration
            ultra_end_hour = min(ultra_end_minutes // 60, 23)
            ultra_end_minute = ultra_end_minutes % 60
            ultra_slot = TimeSlot(first_slot_start, time(ultra_end_hour, ultra_end_minute), base_slot=False)
            combined_slots.append(ultra_slot)
            return combined_slots
        
        for i in range(len(self.DEFAULT_TIME_SLOTS) - 1):
            slot1 = self.DEFAULT_TIME_SLOTS[i]
            slot2 = self.DEFAULT_TIME_SLOTS[i + 1]
            
            if slot1.can_combine_with(slot2):
                combined = TimeSlot.combine_slots(slot1, slot2)
                if combined.fits_duration(required_duration):
                    combined_slots.append(combined)
        
        for i in range(len(self.DEFAULT_TIME_SLOTS) - 2):
            slot1 = self.DEFAULT_TIME_SLOTS[i]
            slot2 = self.DEFAULT_TIME_SLOTS[i + 1]
            slot3 = self.DEFAULT_TIME_SLOTS[i + 2]
            
            if slot1.can_combine_with(slot2) and slot2.can_combine_with(slot3):
                combined_12 = TimeSlot.combine_slots(slot1, slot2)
                combined_123 = TimeSlot.combine_slots(combined_12, slot3)
                if combined_123.fits_duration(required_duration):
                    combined_slots.append(combined_123)
        
        if len(self.DEFAULT_TIME_SLOTS) >= 4:
            slot1, slot2, slot3, slot4 = self.DEFAULT_TIME_SLOTS[:4]
            if (slot1.can_combine_with(slot2) and
                slot2.can_combine_with(slot3) and
                slot3.can_combine_with(slot4)):
                combined_12 = TimeSlot.combine_slots(slot1, slot2)
                combined_123 = TimeSlot.combine_slots(combined_12, slot3)
                combined_1234 = TimeSlot.combine_slots(combined_123, slot4)
                if combined_1234.fits_duration(required_duration):
                    combined_slots.append(combined_1234)
        
        return combined_slots
    
    def filter_classrooms_by_type(self, classrooms: List[Classroom],
                                  required_type: str) -> List[Classroom]:
        if not required_type or required_type.upper() == 'ANY':
            return classrooms
        
        normalized_type = required_type.upper()
        return [c for c in classrooms if c.room_type == normalized_type]
    
    def generate_schedule(
        self, 
        start_date: str, 
        end_date: str,
        department_id: Optional[int] = None,
        exam_type: str = "final",
        clear_existing: bool = False
    ) -> Dict:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError as e:
            return {
                'success': False,
                'scheduled_count': 0,
                'failed_count': 0,
                'failed_courses': [],
                'schedule': [],
                'message': f"Geçersiz tarih formatı: {str(e)}",
                'statistics': {}
            }
        
        if start > end:
            return {
                'success': False,
                'scheduled_count': 0,
                'failed_count': 0,
                'failed_courses': [],
                'schedule': [],
                'message': "Başlangıç tarihi bitiş tarihinden sonra olamaz",
                'statistics': {}
            }
        
        if clear_existing:
            self.exam_repo.delete_planned()
        
        courses = self._get_unscheduled_courses(department_id, exam_type)
        
        if not courses:
            return {
                'success': True,
                'scheduled_count': 0,
                'failed_count': 0,
                'failed_courses': [],
                'schedule': [],
                'message': "Planlanacak ders bulunamadı (tüm dersler zaten planlanmış olabilir)",
                'statistics': {}
            }

        courses = sorted(
            courses, 
            key=lambda x: (x.student_count, x.exam_duration), 
            reverse=True
        )
        
        classrooms = self.classroom_repo.get_all()
        if not classrooms:
            return {
                'success': False,
                'scheduled_count': 0,
                'failed_count': len(courses),
                'failed_courses': [c.code for c in courses],
                'schedule': [],
                'message': "Aktif derslik bulunamadı",
                'statistics': {}
            }
        
        classrooms = sorted(classrooms, key=lambda x: x.capacity, reverse=True)
        
        exam_dates = self._get_weekdays_in_range(start, end)
        
        if not exam_dates:
            return {
                'success': False,
                'scheduled_count': 0,
                'failed_count': len(courses),
                'failed_courses': [c.code for c in courses],
                'schedule': [],
                'message': "Belirtilen tarih aralığında hafta içi gün bulunamadı",
                'statistics': {}
            }
        
        scheduled = []
        failed = []
        failed_reasons = {}
        
        for course in courses:
            result = self._schedule_course(
                course, 
                classrooms, 
                exam_dates, 
                exam_type
            )
            
            if result['success']:
                scheduled.append(result['exam'])
            else:
                failed.append(course)
                failed_reasons[course.code] = result['reason']
        
        stats = self._calculate_statistics(scheduled, exam_dates, classrooms)
        
        if len(failed) == 0:
            message = f"Tüm dersler ({len(scheduled)}) başarıyla planlandı."
            success = True
        elif len(scheduled) == 0:
            message = f"Hiçbir ders planlanamadı. {len(failed)} ders için uygun slot bulunamadı."
            success = False
        else:
            message = f"{len(scheduled)} sınav planlandı, {len(failed)} sınav planlanamadı."
            success = True  # Kısmi başarı
        
        return {
            'success': success,
            'scheduled_count': len(scheduled),
            'failed_count': len(failed),
            'failed_courses': [
                {'code': c.code, 'name': c.name, 'reason': failed_reasons.get(c.code, 'Bilinmiyor')} 
                for c in failed
            ],
            'schedule': [self._exam_to_dict(exam) for exam in scheduled],
            'message': message,
            'statistics': stats
        }
    
    def _schedule_course(
        self,
        course: Course,
        classrooms: List[Classroom],
        dates: List[date],
        exam_type: str
    ) -> Dict:
        student_count = course.student_count or 0
        exam_duration = course.exam_duration or 60
        lecturer_id = course.lecturer_id
        department_id = course.department_id
        course_year = course.year
        
        existing_exams = self.exam_repo.get_by_course_id(course.id)
        active_exams = [e for e in existing_exams if e.status != 'cancelled' and e.exam_type == exam_type]
        if active_exams:
            return {
                'success': False,
                'exam': None,
                'reason': f"Bu ders için zaten bir {exam_type} sınavı planlanmış"
            }
        
        available_days = self._get_lecturer_available_days(lecturer_id)
        
        available_exam_dates = []
        for exam_date in dates:
            day_name = self._get_day_name(exam_date)
            if day_name in available_days:
                available_exam_dates.append(exam_date)
        
        if not available_exam_dates:
            unavailable_days = [d for d in self.WEEKDAYS if d not in available_days]
            return {
                'success': False,
                'exam': None,
                'reason': f"Öğretim üyesi belirtilen tarih aralığında müsait değil. Müsait günler: {', '.join(available_days)}. Tarih aralığında uygun gün yok."
            }
        
        required_room_type = getattr(course, 'required_room_type', 'ANY') or 'ANY'
        required_room_type = 'ANY' if required_room_type == 'STANDART' else required_room_type
        filtered_classrooms = self.filter_classrooms_by_type(classrooms, required_room_type)
        
        suitable_classrooms = [c for c in filtered_classrooms if c.capacity >= student_count]
        
        if not suitable_classrooms:
            combined_result = self._try_combine_classrooms(
                course, classrooms, available_exam_dates, exam_type, available_days
            )
            if combined_result['success']:
                return combined_result
            max_capacity = max([c.capacity for c in classrooms]) if classrooms else 0
            total_capacity = sum([c.capacity for c in classrooms])
            return {
                'success': False,
                'exam': None,
                'reason': f"Yeterli kapasiteli derslik bulunamadı. Öğrenci sayısı: {student_count}, En büyük derslik: {max_capacity}, Toplam kapasite: {total_capacity}"
            }
        
        failure_reasons = {
            'classroom_conflict': 0,
            'student_conflict': 0,
            'lecturer_conflict': 0,
            'slot_duration': 0,
            'room_type_mismatch': 0
        }
        
        appropriate_time_slots = self.get_time_slots_for_duration(exam_duration)
        
        if not appropriate_time_slots:
            max_standard_duration = sum(slot.duration_minutes() for slot in self.DEFAULT_TIME_SLOTS)
            return {
                'success': False,
                'exam': None,
                'reason': f"Sınav süresi ({exam_duration} dk) için uygun zaman bloğu bulunamadı. "
                         f"Maksimum standart süre: {max_standard_duration} dk. "
                         f"Daha uzun sınavlar için gün içinde dinamik slot oluşturulur, "
                         f"ancak gün sonuna sarkan sınavlar uygun olmayabilir."
            }
        
        for exam_date in available_exam_dates:
            for time_slot in appropriate_time_slots:
                actual_end_time = self._calculate_end_time(time_slot.start_time, exam_duration)
                
                for classroom in suitable_classrooms:
                    conflict = self._check_all_conflicts(
                        course_id=course.id,
                        classroom_id=classroom.id,
                        exam_date=exam_date,
                        start_time=time_slot.start_time,
                        end_time=actual_end_time,
                        department_id=department_id,
                        course_year=course_year,
                        lecturer_id=lecturer_id
                    )
                    
                    if conflict['has_conflict']:
                        reason = conflict.get('reason', '')
                        if 'Derslik' in reason:
                            failure_reasons['classroom_conflict'] += 1
                        elif 'Öğrenci' in reason:
                            failure_reasons['student_conflict'] += 1
                        elif 'Hoca' in reason:
                            failure_reasons['lecturer_conflict'] += 1
                        continue
                    
                    exam = ExamSchedule(
                        course_id=course.id,
                        classroom_id=classroom.id,
                        exam_date=exam_date,
                        start_time=time_slot.start_time,
                        end_time=actual_end_time,
                        exam_type=exam_type,
                        status="planned",
                        notes=f"Otomatik planlandı - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        course_code=course.code,
                        course_name=course.name,
                        classroom_name=classroom.name,
                        faculty_name=classroom.faculty_name,
                        student_count=student_count
                    )
                    
                    try:
                        exam_id = self.exam_repo.create(exam)
                        exam.id = exam_id
                        return {
                            'success': True,
                            'exam': exam,
                            'reason': None
                        }
                    except Exception as e:
                        continue
        
        reason_parts = []
        if failure_reasons['classroom_conflict'] > 0:
            reason_parts.append(f"Derslik çakışması: {failure_reasons['classroom_conflict']}")
        if failure_reasons['student_conflict'] > 0:
            conflict_type = 'öğrenci ID kesişimi' if self.use_student_based_conflict else 'aynı bölüm/yıl'
            reason_parts.append(f"Öğrenci çakışması ({conflict_type}): {failure_reasons['student_conflict']}")
        if failure_reasons['lecturer_conflict'] > 0:
            reason_parts.append(f"Hoca çakışması: {failure_reasons['lecturer_conflict']}")
        if failure_reasons['room_type_mismatch'] > 0:
            reason_parts.append(f"Oda tipi uyuşmazlığı: {failure_reasons['room_type_mismatch']}")
        
        if reason_parts:
            room_type_info = f" (Gereken tip: {required_room_type})" if required_room_type != 'ANY' else ""
            detailed_reason = f"Tüm slotlar dolu{room_type_info}. Denenen: {len(available_exam_dates)} gün x {len(appropriate_time_slots)} slot x {len(suitable_classrooms)} derslik. " + ", ".join(reason_parts)
        else:
            detailed_reason = f"Uygun slot bulunamadı. Müsait gün sayısı: {len(available_exam_dates)}, Uygun derslik: {len(suitable_classrooms)}"
        
        return {
            'success': False,
            'exam': None,
            'reason': detailed_reason
        }
    
    def _try_combine_classrooms(
        self,
        course: Course,
        classrooms: List[Classroom],
        dates: List[date],
        exam_type: str,
        available_days: List[str]
    ) -> Dict:
        student_count = course.student_count or 0
        exam_duration = course.exam_duration or 60
        lecturer_id = course.lecturer_id
        department_id = course.department_id
        course_year = course.year
        
        required_room_type = getattr(course, 'required_room_type', 'ANY') or 'ANY'
        required_room_type = 'ANY' if required_room_type == 'STANDART' else required_room_type
        filtered_classrooms = self.filter_classrooms_by_type(classrooms, required_room_type)
        
        sorted_classrooms = sorted(filtered_classrooms, key=lambda x: x.capacity, reverse=True)
        
        appropriate_time_slots = self.get_time_slots_for_duration(exam_duration)
        
        if not appropriate_time_slots:
            max_standard_duration = sum(slot.duration_minutes() for slot in self.DEFAULT_TIME_SLOTS)
            return {
                'success': False,
                'exam': None,
                'reason': f"Sınav süresi ({exam_duration} dk) için uygun zaman bloğu bulunamadı. "
                         f"Maksimum standart süre: {max_standard_duration} dk."
            }
        
        for exam_date in dates:
            for time_slot in appropriate_time_slots:
                actual_end_time = self._calculate_end_time(time_slot.start_time, exam_duration)
                
                available_classrooms = []
                for classroom in sorted_classrooms:
                    if self._has_classroom_conflict(classroom.id, exam_date, time_slot.start_time, actual_end_time):
                        continue
                    available_classrooms.append(classroom)
                
                if not available_classrooms:
                    continue
                
                if self.use_student_based_conflict:
                    if self._has_student_conflict(
                        0, None, exam_date,  # department_id ve course_year kullanılmıyor
                        time_slot.start_time, actual_end_time, course.id, course.id
                    ):
                        continue
                elif department_id:
                    if self._has_student_conflict(
                        department_id, course_year, exam_date,
                        time_slot.start_time, actual_end_time, course.id, course.id
                    ):
                        continue
                
                if lecturer_id and self._has_lecturer_conflict(
                    lecturer_id, exam_date, time_slot.start_time, actual_end_time
                ):
                    continue
                
                selected_classrooms = self._select_nearby_classrooms(
                    available_classrooms, student_count
                )
                
                if not selected_classrooms:
                    continue
                
                total_capacity = sum(c.capacity for c in selected_classrooms)
                
                if total_capacity < student_count:
                    continue
                
                combined_classroom_names = ", ".join([c.name for c in selected_classrooms])
                primary_classroom = selected_classrooms[0]
                notes_text = f"Otomatik planlandı (Yakın Birleşik Derslikler: {combined_classroom_names}) - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
                exam = ExamSchedule(
                    course_id=course.id,
                    classroom_id=primary_classroom.id,
                    exam_date=exam_date,
                    start_time=time_slot.start_time,
                    end_time=actual_end_time,
                    exam_type=exam_type,
                    status="planned",
                    notes=notes_text,
                    course_code=course.code,
                    course_name=course.name,
                    classroom_name=combined_classroom_names,
                    faculty_name=primary_classroom.faculty_name,
                    student_count=student_count
                )
                
                try:
                    exam_id = self.exam_repo.create(exam)
                    exam.id = exam_id
                    
                    for i, additional_classroom in enumerate(selected_classrooms[1:], start=2):
                        additional_exam = ExamSchedule(
                            course_id=course.id,
                            classroom_id=additional_classroom.id,
                            exam_date=exam_date,
                            start_time=time_slot.start_time,
                            end_time=actual_end_time,
                            exam_type=exam_type,
                            status="planned",
                            notes=f"Birleşik sınav ({i}/{len(selected_classrooms)}) - Ana derslik: {primary_classroom.name} - {notes_text}",
                            course_code=course.code,
                            course_name=course.name,
                            classroom_name=additional_classroom.name,
                            faculty_name=additional_classroom.faculty_name,
                            student_count=0
                        )
                        self.exam_repo.create(additional_exam)
                    
                    return {
                        'success': True,
                        'exam': exam,
                        'reason': None
                    }
                except Exception as e:
                    continue
        
        conflict_details = []
        if self.use_student_based_conflict:
            conflict_details.append("öğrenci ID kesişimi kontrolü aktif")
        else:
            conflict_details.append("bölüm/yıl kontrolü aktif")
        
        reason = (f"Yakın derslikler birleştirilerek de yeterli kapasite sağlanamadı ({student_count} öğrenci). "
                 f"Olası nedenler: Çakışan sınavlar, yetersiz müsait derslik, "
                 f"veya {', '.join(conflict_details)}.")
        
        return {
            'success': False,
            'exam': None,
            'reason': reason
        }
    
    def _select_nearby_classrooms(
        self,
        available_classrooms: List[Classroom],
        required_capacity: int
    ) -> List[Classroom]:
        if not available_classrooms:
            return []
        
        primary_classroom = max(available_classrooms, key=lambda c: c.capacity)
        selected = [primary_classroom]
        current_capacity = primary_classroom.capacity
        
        available_names = [c.name for c in available_classrooms if c != primary_classroom]
        
        primary_name = primary_classroom.name
        
        neighbors = self.proximity_loader.get_available_neighbors_for_combination(
            primary_name, available_names
        )
        
        for neighbor_name in neighbors:
            neighbor = next((c for c in available_classrooms if c.name == neighbor_name), None)
            if neighbor and neighbor not in selected:
                selected.append(neighbor)
                current_capacity += neighbor.capacity
                if current_capacity >= required_capacity:
                    break
        
        if current_capacity < required_capacity:
            primary_block = self.proximity_loader.get_block(primary_name)
            if primary_block:
                same_block_classrooms = self.proximity_loader.get_classrooms_in_block(primary_block)
                for classroom_name in same_block_classrooms:
                    if classroom_name in available_names:
                        classroom = next((c for c in available_classrooms if c.name == classroom_name), None)
                        if classroom and classroom not in selected:
                            selected.append(classroom)
                            current_capacity += classroom.capacity
                            if current_capacity >= required_capacity:
                                break
        
        if current_capacity < required_capacity:
            remaining = [c for c in available_classrooms if c not in selected]
            remaining.sort(key=lambda c: c.capacity, reverse=True)
            for classroom in remaining:
                selected.append(classroom)
                current_capacity += classroom.capacity
                if current_capacity >= required_capacity:
                    break
        
        selected.sort(key=lambda c: c.capacity, reverse=True)
        
        return selected
    
    def _check_all_conflicts(
        self,
        course_id: int,
        classroom_id: int,
        exam_date: date,
        start_time: time,
        end_time: time,
        department_id: Optional[int],
        course_year: Optional[int],
        lecturer_id: Optional[int]
    ) -> Dict:
        start_str = start_time.strftime('%H:%M') if isinstance(start_time, time) else str(start_time)
        end_str = end_time.strftime('%H:%M') if isinstance(end_time, time) else str(end_time)
        
        if self._has_classroom_conflict(classroom_id, exam_date, start_time, end_time):
            return {'has_conflict': True, 'reason': 'Derslik çakışması'}
        
        if self._has_student_conflict(
            department_id, course_year, exam_date, start_time, end_time, course_id, course_id
        ):
            conflict_type = 'öğrenci ID kesişimi' if self.use_student_based_conflict else 'aynı bölüm/yıl'
            return {'has_conflict': True, 'reason': f'Öğrenci çakışması ({conflict_type})'}
        
        if lecturer_id and self._has_lecturer_conflict(lecturer_id, exam_date, start_time, end_time):
            return {'has_conflict': True, 'reason': 'Hoca çakışması'}
        
        return {'has_conflict': False, 'reason': None}
    
    def _has_classroom_conflict(
        self, 
        classroom_id: int, 
        exam_date: date, 
        start_time: time, 
        end_time: time
    ) -> bool:
        existing_exams = self.exam_repo.get_by_classroom_and_date(classroom_id, exam_date)
        
        for exam in existing_exams:
            if self._times_overlap(start_time, end_time, exam.start_time, exam.end_time):
                return True
        
        return False
    
    def _has_student_conflict(
        self,
        department_id: int,
        course_year: Optional[int],
        exam_date: date,
        start_time: time,
        end_time: time,
        exclude_course_id: int,
        course_id: Optional[int] = None
    ) -> bool:

        if course_id is None:
            course_id = exclude_course_id
        
        if self.use_student_based_conflict and course_id:
            return self._has_student_conflict_based_on_students(
                course_id, exam_date, start_time, end_time
            )
        
        existing_exams = self.exam_repo.get_by_department_and_date(department_id, exam_date)
        
        for exam in existing_exams:
            if exam.course_id == exclude_course_id:
                continue
            
            if not self._times_overlap(start_time, end_time, exam.start_time, exam.end_time):
                continue
            
            exam_course_year = getattr(exam, 'course_year', None)
            
            if course_year is None or exam_course_year is None or course_year == exam_course_year:
                return True
        
        return False
    
    def _has_student_conflict_based_on_students(
        self,
        course_id: int,
        exam_date: date,
        start_time: time,
        end_time: time
    ) -> bool:

        students_of_course = self._get_students_for_course(course_id)
        
        if not students_of_course:
            import logging
            logging.warning(f"Ders ID {course_id} için öğrenci verisi bulunamadı. Çakışma kontrolü atlanıyor.")
            return False
        
        existing_exams = self.exam_repo.get_by_date(exam_date)
        
        conflicting_exam_course_ids = []
        for exam in existing_exams:
            if exam.course_id == course_id:
                continue
            
            if self._times_overlap(start_time, end_time, exam.start_time, exam.end_time):
                conflicting_exam_course_ids.append(exam.course_id)
        
        for other_course_id in conflicting_exam_course_ids:
            students_of_other_course = self._get_students_for_course(other_course_id)
            
            intersection = students_of_course & students_of_other_course
            
            if intersection:
                return True
        
        return False
    
    def _get_students_for_course(self, course_id: int) -> Set[int]:
        if course_id in self._course_student_cache:
            return self._course_student_cache[course_id]
        
        try:
            student_ids = self.student_course_repo.get_student_ids_by_course(course_id)
            self._course_student_cache[course_id] = student_ids
            return student_ids
        except Exception as e:
            print(f"Uyarı: {course_id} numaralı ders için öğrenci verisi alınamadı: {e}")
            return set()
    
    def clear_student_cache(self):
        self._course_student_cache.clear()
    
    def _has_lecturer_conflict(
        self,
        lecturer_id: int,
        exam_date: date,
        start_time: time,
        end_time: time
    ) -> bool:
        existing_exams = self.exam_repo.get_by_lecturer_and_date(lecturer_id, exam_date)
        
        for exam in existing_exams:
            if self._times_overlap(start_time, end_time, exam.start_time, exam.end_time):
                return True
        
        return False
    
    def _times_overlap(
        self, 
        start1: time, 
        end1: time, 
        start2: time, 
        end2: time
    ) -> bool:
        s1 = self._time_to_minutes(start1)
        e1 = self._time_to_minutes(end1)
        s2 = self._time_to_minutes(start2)
        e2 = self._time_to_minutes(end2)
        
        return not (e1 <= s2 or e2 <= s1)
    
    def _time_to_minutes(self, t) -> int:
        if isinstance(t, time):
            return t.hour * 60 + t.minute
        if isinstance(t, str):
            parts = t.split(':')
            return int(parts[0]) * 60 + int(parts[1])
        return 0
    
    def _calculate_end_time(self, start: time, duration_minutes: int) -> time:
        start_minutes = start.hour * 60 + start.minute
        end_minutes = start_minutes + duration_minutes
        
        hours = end_minutes // 60
        minutes = end_minutes % 60
        
        if hours >= 24:
            hours = 23
            minutes = 59
        
        return time(hours, minutes)
    
    def _get_weekdays_in_range(self, start: date, end: date) -> List[date]:
        weekdays = []
        current = start
        
        while current <= end:
            if current.weekday() < 5:
                weekdays.append(current)
            current += timedelta(days=1)
        
        return weekdays
    
    def _get_day_name(self, d: date) -> str:
        return self.WEEKDAYS[d.weekday()]
    
    def _normalize_day_name(self, day: str) -> str:
        if not day:
            return day
        
        day_lower = day.lower().strip()
        
        if day_lower in self.DAY_ALIASES:
            return self.DAY_ALIASES[day_lower]
        
        return day
    
    def _get_lecturer_available_days(self, lecturer_id: Optional[int]) -> List[str]:
        if not lecturer_id:
            return list(DEFAULT_AVAILABLE_DAYS)
        
        try:
            lecturer = self.lecturer_repo.get_by_id(lecturer_id)
            if lecturer and lecturer.available_days:
                normalized_days = []
                for day in lecturer.available_days:
                    normalized = self._normalize_day_name(day)
                    if normalized not in normalized_days:
                        normalized_days.append(normalized)
                return normalized_days
        except Exception:
            pass
        
        return list(DEFAULT_AVAILABLE_DAYS)
    
    def _get_unscheduled_courses(self, department_id: Optional[int] = None, exam_type: str = None) -> List[Course]:
        courses = self.course_repo.get_unscheduled_courses(exam_type=exam_type)
        
        if department_id:
            courses = [c for c in courses if c.department_id == department_id]
        
        return courses
    
    def _exam_to_dict(self, exam: ExamSchedule) -> Dict:
        return {
            'id': exam.id,
            'course_id': exam.course_id,
            'course_code': exam.course_code,
            'course_name': exam.course_name,
            'classroom_id': exam.classroom_id,
            'classroom_name': exam.classroom_name,
            'faculty_name': exam.faculty_name,
            'exam_date': exam.exam_date.isoformat() if exam.exam_date else None,
            'start_time': exam.start_time.strftime('%H:%M') if exam.start_time else None,
            'end_time': exam.end_time.strftime('%H:%M') if exam.end_time else None,
            'exam_type': exam.exam_type,
            'status': exam.status,
            'student_count': exam.student_count
        }
    
    def _calculate_statistics(
        self, 
        scheduled: List[ExamSchedule], 
        dates: List[date],
        classrooms: List[Classroom]
    ) -> Dict:
        if not scheduled:
            return {
                'total_exams': 0,
                'total_students': 0,
                'exams_by_date': {},
                'exams_by_classroom': {},
                'utilization_rate': 0
            }
        
        exams_by_date = {}
        exams_by_classroom = {}
        total_students = 0
        
        for exam in scheduled:
            date_str = exam.exam_date.isoformat() if exam.exam_date else 'unknown'
            exams_by_date[date_str] = exams_by_date.get(date_str, 0) + 1
            
            classroom_name = exam.classroom_name or 'unknown'
            exams_by_classroom[classroom_name] = exams_by_classroom.get(classroom_name, 0) + 1
            
            total_students += exam.student_count or 0
        
        total_slots = len(dates) * len(self.time_slots) * len(classrooms)
        utilization_rate = (len(scheduled) / total_slots * 100) if total_slots > 0 else 0
        
        return {
            'total_exams': len(scheduled),
            'total_students': total_students,
            'exams_by_date': exams_by_date,
            'exams_by_classroom': exams_by_classroom,
            'utilization_rate': round(utilization_rate, 2)
        }
    
    def validate_manual_schedule(
        self,
        course_id: int,
        classroom_id: int,
        exam_date: str,
        start_time: str,
        end_time: str = None
    ) -> Dict:
        errors = []
        warnings = []
        
        try:
            exam_date_obj = datetime.strptime(exam_date, '%Y-%m-%d').date()
        except ValueError:
            errors.append("Geçersiz tarih formatı (YYYY-MM-DD olmalı)")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        try:
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
        except ValueError:
            errors.append("Geçersiz başlangıç saati formatı (HH:MM olmalı)")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        course = self.course_repo.get_by_id(course_id)
        if not course:
            errors.append("Ders bulunamadı")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        classroom = self.classroom_repo.get_by_id(classroom_id)
        if not classroom:
            errors.append("Derslik bulunamadı")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        if end_time:
            try:
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            except ValueError:
                errors.append("Geçersiz bitiş saati formatı (HH:MM olmalı)")
                return {'valid': False, 'errors': errors, 'warnings': warnings}
        else:
            end_time_obj = self._calculate_end_time(start_time_obj, course.exam_duration or 60)
        
        if exam_date_obj.weekday() >= 5:
            warnings.append("Seçilen tarih hafta sonu")
        
        if classroom.capacity < (course.student_count or 0):
            errors.append(
                f"Derslik kapasitesi yetersiz ({classroom.capacity} < {course.student_count})"
            )
        
        if course.lecturer_id:
            available_days = self._get_lecturer_available_days(course.lecturer_id)
            day_name = self._get_day_name(exam_date_obj)
            if day_name not in available_days:
                errors.append(f"Öğretim görevlisi {day_name} günü müsait değil")
        
        conflicts = self._check_all_conflicts(
            course_id=course_id,
            classroom_id=classroom_id,
            exam_date=exam_date_obj,
            start_time=start_time_obj,
            end_time=end_time_obj,
            department_id=course.department_id,
            course_year=course.year,
            lecturer_id=course.lecturer_id
        )
        
        if conflicts['has_conflict']:
            errors.append(f"Çakışma tespit edildi: {conflicts['reason']}")
        
        existing = self.exam_repo.get_by_course_id(course_id)
        active_exams = [e for e in existing if e.status != 'cancelled']
        if active_exams:
            warnings.append("Bu ders için zaten planlanmış bir sınav var")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def clear_schedule(self, start_date: str = None, end_date: str = None) -> Dict:
        try:
            if start_date and end_date:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                schedules = self.exam_repo.get_by_date_range(start, end)
                planned = [s for s in schedules if s.status == 'planned']
                
                deleted_count = 0
                for schedule in planned:
                    if self.exam_repo.delete(schedule.id):
                        deleted_count += 1
                
                return {
                    'success': True,
                    'deleted_count': deleted_count,
                    'message': f"{deleted_count} planlanmış sınav silindi"
                }
            else:
                deleted_count = self.exam_repo.delete_planned()
                return {
                    'success': True,
                    'deleted_count': deleted_count or 0,
                    'message': f"Tüm planlanmış sınavlar silindi"
                }
        except Exception as e:
            return {
                'success': False,
                'deleted_count': 0,
                'message': f"Hata: {str(e)}"
            }
    
    def get_schedule_statistics(self, start_date: str = None, end_date: str = None) -> Dict:
        try:
            if start_date and end_date:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                schedules = self.exam_repo.get_by_date_range(start, end)
            else:
                schedules = self.exam_repo.get_all_with_details()
        except Exception:
            schedules = []
        
        stats = {
            'total': len(schedules),
            'planned': len([s for s in schedules if s.status == 'planned']),
            'confirmed': len([s for s in schedules if s.status == 'confirmed']),
            'cancelled': len([s for s in schedules if s.status == 'cancelled']),
            'by_date': {},
            'by_classroom': {},
            'by_department': {}
        }
        
        for schedule in schedules:
            date_str = str(schedule.exam_date) if schedule.exam_date else 'unknown'
            stats['by_date'][date_str] = stats['by_date'].get(date_str, 0) + 1
            
            classroom_name = schedule.classroom_name or 'unknown'
            stats['by_classroom'][classroom_name] = stats['by_classroom'].get(classroom_name, 0) + 1
            
            dept_name = schedule.department_name or 'unknown'
            stats['by_department'][dept_name] = stats['by_department'].get(dept_name, 0) + 1
        
        return stats
    
    def set_time_slots(self, slots: List[Tuple[str, str]]) -> None:
        self.time_slots = []
        for start_str, end_str in slots:
            start = datetime.strptime(start_str, '%H:%M').time()
            end = datetime.strptime(end_str, '%H:%M').time()
            self.time_slots.append(TimeSlot(start, end))
    
    def reset_time_slots(self) -> None:
        self.time_slots = self.DEFAULT_TIME_SLOTS
