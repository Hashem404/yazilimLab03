"""
Sınav programı servisi
"""

from typing import List, Optional, Tuple, Set
from datetime import date, time, datetime
from src.models.exam_schedule import ExamSchedule
from src.repositories.exam_schedule_repository import ExamScheduleRepository
from src.repositories.course_repository import CourseRepository
from src.repositories.classroom_repository import ClassroomRepository
from src.repositories.lecturer_repository import LecturerRepository
from src.repositories.student_repository import StudentCourseRepository


WEEKDAY_NAMES = {
    0: 'Pazartesi',
    1: 'Salı',
    2: 'Çarşamba',
    3: 'Perşembe',
    4: 'Cuma',
    5: 'Cumartesi',
    6: 'Pazar'
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
    'cuma': 'Cuma',
    'cumartesi': 'Cumartesi',
    'pazar': 'Pazar'
}


class ExamScheduleService:
    
    def __init__(self, use_student_based_conflict: bool = True):
        self.repository = ExamScheduleRepository()
        self.course_repo = CourseRepository()
        self.classroom_repo = ClassroomRepository()
        self.lecturer_repo = LecturerRepository()
        self.student_course_repo = StudentCourseRepository()
        
        self.use_student_based_conflict = use_student_based_conflict
        
        self._course_student_cache: dict = {}
    
    def get_all(self) -> List[ExamSchedule]:
        return self.repository.get_all_with_details()
    
    def get_by_id(self, schedule_id: int) -> Optional[ExamSchedule]:
        return self.repository.get_by_id(schedule_id)
    
    def get_by_date(self, exam_date: date) -> List[ExamSchedule]:
        return self.repository.get_by_date(exam_date)
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[ExamSchedule]:
        return self.repository.get_by_date_range(start_date, end_date)
    
    def get_by_course_id(self, course_id: int) -> List[ExamSchedule]:
        return self.repository.get_by_course_id(course_id)
    
    def get_by_department_id(self, department_id: int) -> List[ExamSchedule]:
        return self.repository.get_by_department_id(department_id)
    
    def get_by_faculty_id(self, faculty_id: int) -> List[ExamSchedule]:
        return self.repository.get_by_faculty_id(faculty_id)
    
    
    def get_by_student_id(self, student_id: int) -> List[ExamSchedule]:
        return self.repository.get_by_student_id(student_id)
    
    def get_by_student_number(self, student_number: str) -> List[ExamSchedule]:

        return self.repository.get_by_student_number(student_number)
    
    def get_by_lecturer_all(self, lecturer_id: int) -> List[ExamSchedule]:

        return self.repository.get_by_lecturer_id_all(lecturer_id)
    
    def _get_day_name(self, exam_date: date) -> str:
        return WEEKDAY_NAMES.get(exam_date.weekday(), '')
    
    def _normalize_day_name(self, day: str) -> str:
        if not day:
            return day
        
        day_lower = day.lower().strip()
        
        if day_lower in DAY_ALIASES:
            return DAY_ALIASES[day_lower]
        
        return day
    
    def _normalize_available_days(self, days: list) -> list:
        if not days:
            return []
        
        normalized = []
        for day in days:
            norm_day = self._normalize_day_name(day)
            if norm_day not in normalized:
                normalized.append(norm_day)
        return normalized
    
    def _calculate_duration_minutes(self, start_time: time, end_time: time) -> int:
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        return end_minutes - start_minutes
    
    def _check_student_conflict_with_courses(
        self,
        course_id: int,
        exam_date: date,
        start_time: time,
        end_time: time,
        exclude_id: int = None
    ) -> Tuple[bool, str]:
        """
        Gerçek öğrenci listeleri üzerinden çakışma kontrolü
        
        Args:
            course_id: Kontrol edilecek dersin ID'si
            exam_date: Sınav tarihi
            start_time: Başlangıç saati
            end_time: Bitiş saati
            exclude_id: Hariç tutulacak sınav ID'si
            
        Returns:
            Tuple[bool, str]: (Çakışma var mı?, Hata mesajı)
        """
        students_of_course = self._get_students_for_course(course_id)
        
        if not students_of_course:
            return False, ""
        
        existing_exams = self.repository.get_by_date(exam_date)
        
        start_time_str = start_time.strftime('%H:%M') if isinstance(start_time, time) else str(start_time)[:5]
        end_time_str = end_time.strftime('%H:%M') if isinstance(end_time, time) else str(end_time)[:5]
        
        for exam in existing_exams:
            if exam.course_id == course_id or (exclude_id and exam.id == exclude_id):
                continue
            
            if not self._times_overlap(start_time_str, end_time_str,
                                      exam.start_time.strftime('%H:%M'),
                                      exam.end_time.strftime('%H:%M')):
                continue
            
            students_of_other_course = self._get_students_for_course(exam.course_id)
            intersection = students_of_course & students_of_other_course
            
            if intersection:
                overlap_count = len(intersection)
                return True, f"Öğrenci çakışması var! '{exam.course_code} - {exam.course_name}' dersi ile {overlap_count} ortak öğrenci var. Bir öğrencinin aynı saatte iki sınavı olamaz."
        
        return False, ""
    
    def _get_students_for_course(self, course_id: int) -> Set[int]:
        if course_id in self._course_student_cache:
            return self._course_student_cache[course_id]
        
        try:
            student_ids = self.student_course_repo.get_student_ids_by_course(course_id)
            self._course_student_cache[course_id] = student_ids
            return student_ids
        except Exception:
            return set()
    
    def _times_overlap(self, start1: str, end1: str, start2: str, end2: str) -> bool:
        s1 = int(start1[:2]) * 60 + int(start1[3:])
        e1 = int(end1[:2]) * 60 + int(end1[3:])
        s2 = int(start2[:2]) * 60 + int(start2[3:])
        e2 = int(end2[:2]) * 60 + int(end2[3:])
        return not (e1 <= s2 or e2 <= s1)
    
    def clear_student_cache(self):
        self._course_student_cache.clear()
    
    def validate_exam_constraints(
        self,
        course_id: int,
        classroom_id: int,
        exam_date: date,
        start_time: time,
        end_time: time,
        exam_type: str = "final",
        exclude_id: int = None,
        skip_course_exam_check: bool = False,
        skip_capacity_check: bool = False
    ) -> Tuple[bool, str]:
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return False, "Ders bulunamadı."
        
        classroom = self.classroom_repo.get_by_id(classroom_id)
        if not classroom:
            return False, "Derslik bulunamadı."
        
        start_time_str = start_time.strftime('%H:%M') if isinstance(start_time, time) else str(start_time)[:5]
        end_time_str = end_time.strftime('%H:%M') if isinstance(end_time, time) else str(end_time)[:5]
        
        if not skip_course_exam_check:
            if self.repository.check_course_exam_exists(course_id, exam_type, exclude_id):
                exam_type_labels = {
                    'midterm': 'Vize',
                    'final': 'Final',
                    'makeup': 'Bütünleme',
                    'quiz': 'Quiz'
                }
                exam_label = exam_type_labels.get(exam_type, exam_type)
                return False, f"Bu ders için zaten bir {exam_label} sınavı planlanmış. Bir ders için birden fazla sınav saati atanamaz."
        
        if self.repository.check_conflict(classroom_id, exam_date, start_time_str, end_time_str, exclude_id):
            return False, f"Bu derslik ({classroom.name}) belirtilen tarih ve saatte başka bir sınav için ayrılmış. Bir derslikte aynı anda birden fazla sınav yapılamaz."
        
        if self.use_student_based_conflict:
            has_conflict, error_msg = self._check_student_conflict_with_courses(
                course_id, exam_date, start_time, end_time, exclude_id
            )
            if has_conflict:
                return False, error_msg
        elif course.department_id and course.year:
            conflicting_exams = self.repository.check_student_conflict(
                department_id=course.department_id,
                course_year=course.year,
                exam_date=exam_date,
                start_time=start_time_str,
                end_time=end_time_str,
                exclude_course_id=course_id,
                exclude_id=exclude_id
            )
            if conflicting_exams:
                conflict = conflicting_exams[0]
                return False, f"Aynı bölüm ve yıldaki öğrenciler için saat çakışması var. '{conflict.course_code} - {conflict.course_name}' dersi ile çakışıyor. Bir öğrencinin aynı saatte iki sınavı olamaz."
        
        if not skip_capacity_check:
            student_count = course.student_count or 0
            if student_count > classroom.capacity:
                return False, f"Öğrenci sayısı ({student_count}) derslik kapasitesini ({classroom.capacity}) aşıyor. Sınav, derslik kapasitesinden fazla öğrenciye atanamaz."
        
        if course.lecturer_id:
            lecturer = self.lecturer_repo.get_by_id(course.lecturer_id)
            if lecturer:
                day_name = self._get_day_name(exam_date)
                if day_name and lecturer.available_days:
                    normalized_available_days = self._normalize_available_days(lecturer.available_days)
                    if day_name not in normalized_available_days:
                        return False, f"Öğretim üyesi ({lecturer.full_name}) bu gün ({day_name}) müsait değil. Hoca yalnızca müsait olduğu günlerde ({', '.join(normalized_available_days)}) sınava girebilir."
                
                lecturer_conflicts = self.repository.check_lecturer_conflict(
                    lecturer_id=course.lecturer_id,
                    exam_date=exam_date,
                    start_time=start_time_str,
                    end_time=end_time_str,
                    exclude_id=exclude_id
                )
                if lecturer_conflicts:
                    conflict = lecturer_conflicts[0]
                    return False, f"Öğretim üyesinin ({lecturer.full_name}) bu saatte başka bir sınavı var: '{conflict.course_code} - {conflict.course_name}'"
        
        if course.exam_duration and course.exam_duration > 0:
            planned_duration = self._calculate_duration_minutes(start_time, end_time)
            if planned_duration < course.exam_duration:
                return False, f"Planlanan süre ({planned_duration} dk) dersin sınav süresinden ({course.exam_duration} dk) kısa. Belirtilen sınav süresi dışında planlama yapılamaz."
            if planned_duration > course.exam_duration + 30:
                return False, f"Planlanan süre ({planned_duration} dk) dersin sınav süresinden ({course.exam_duration} dk) çok fazla. Lütfen sınav süresine uygun bir zaman aralığı seçin."
        
        if hasattr(classroom, 'is_suitable') and not classroom.is_suitable:
            return False, f"Bu derslik ({classroom.name}) sınav için uygun değil."
        
        return True, ""
    
    def validate_multi_classroom_exam(
        self,
        course_id: int,
        classroom_ids: List[int],
        exam_date: date,
        start_time: time,
        end_time: time,
        exam_type: str = "final",
        exclude_id: int = None
    ) -> Tuple[bool, str]:
        if not classroom_ids:
            return False, "En az bir derslik seçilmelidir."
        
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return False, "Ders bulunamadı."
        
        if self.repository.check_course_exam_exists(course_id, exam_type, exclude_id):
            exam_type_labels = {
                'midterm': 'Vize',
                'final': 'Final',
                'makeup': 'Bütünleme',
                'quiz': 'Quiz'
            }
            exam_label = exam_type_labels.get(exam_type, exam_type)
            return False, f"Bu ders için zaten bir {exam_label} sınavı planlanmış."
        
        total_capacity = 0
        classrooms = []
        for cid in classroom_ids:
            classroom = self.classroom_repo.get_by_id(cid)
            if not classroom:
                return False, f"Derslik (ID: {cid}) bulunamadı."
            if hasattr(classroom, 'is_suitable') and not classroom.is_suitable:
                return False, f"Derslik ({classroom.name}) sınav için uygun değil."
            classrooms.append(classroom)
            total_capacity += classroom.capacity
        
        student_count = course.student_count or 0
        if student_count > total_capacity:
            return False, f"Toplam derslik kapasitesi ({total_capacity}) öğrenci sayısından ({student_count}) az. Daha fazla derslik seçin."
        
        start_time_str = start_time.strftime('%H:%M') if isinstance(start_time, time) else str(start_time)[:5]
        end_time_str = end_time.strftime('%H:%M') if isinstance(end_time, time) else str(end_time)[:5]
        
        for classroom in classrooms:
            if self.repository.check_conflict(classroom.id, exam_date, start_time_str, end_time_str, exclude_id):
                return False, f"Derslik ({classroom.name}) belirtilen tarih ve saatte başka bir sınav için ayrılmış."
        
        if self.use_student_based_conflict:
            has_conflict, error_msg = self._check_student_conflict_with_courses(
                course_id, exam_date, start_time, end_time, exclude_id
            )
            if has_conflict:
                return False, error_msg
        elif course.department_id and course.year:
            conflicting_exams = self.repository.check_student_conflict(
                department_id=course.department_id,
                course_year=course.year,
                exam_date=exam_date,
                start_time=start_time_str,
                end_time=end_time_str,
                exclude_course_id=course_id,
                exclude_id=exclude_id
            )
            if conflicting_exams:
                conflict = conflicting_exams[0]
                return False, f"Aynı bölüm ve yıldaki öğrenciler için saat çakışması var: '{conflict.course_code}'"
        
        if course.lecturer_id:
            lecturer = self.lecturer_repo.get_by_id(course.lecturer_id)
            if lecturer:
                day_name = self._get_day_name(exam_date)
                if day_name and lecturer.available_days:
                    normalized_available_days = self._normalize_available_days(lecturer.available_days)
                    if day_name not in normalized_available_days:
                        return False, f"Öğretim üyesi ({lecturer.full_name}) bu gün ({day_name}) müsait değil. Müsait günler: {', '.join(normalized_available_days)}"
                
                lecturer_conflicts = self.repository.check_lecturer_conflict(
                    lecturer_id=course.lecturer_id,
                    exam_date=exam_date,
                    start_time=start_time_str,
                    end_time=end_time_str,
                    exclude_id=exclude_id
                )
                if lecturer_conflicts:
                    conflict = lecturer_conflicts[0]
                    return False, f"Öğretim üyesinin bu saatte başka bir sınavı var: '{conflict.course_code}'"
        
        if course.exam_duration and course.exam_duration > 0:
            planned_duration = self._calculate_duration_minutes(start_time, end_time)
            if planned_duration < course.exam_duration:
                return False, f"Planlanan süre ({planned_duration} dk) sınav süresinden ({course.exam_duration} dk) kısa."
            if planned_duration > course.exam_duration + 30:
                return False, f"Planlanan süre ({planned_duration} dk) sınav süresinden ({course.exam_duration} dk) çok fazla."
        
        return True, ""
    
    def create(self, course_id: int, classroom_id: int, exam_date: date,
               start_time: time, end_time: time, exam_type: str = "final",
               notes: str = None) -> Tuple[bool, str, Optional[int]]:
        if not course_id:
            return False, "Ders seçimi gereklidir.", None
        
        if not classroom_id:
            return False, "Derslik seçimi gereklidir.", None
        
        if start_time >= end_time:
            return False, "Bitiş saati başlangıç saatinden sonra olmalıdır.", None
        
        is_valid, error_message = self.validate_exam_constraints(
            course_id=course_id,
            classroom_id=classroom_id,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time,
            exam_type=exam_type,
            exclude_id=None
        )
        
        if not is_valid:
            return False, error_message, None
        
        exam_schedule = ExamSchedule(
            course_id=course_id,
            classroom_id=classroom_id,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time,
            exam_type=exam_type,
            status="planned",
            notes=notes.strip() if notes else None
        )
        
        try:
            schedule_id = self.repository.create(exam_schedule)
            self.clear_student_cache()
            return True, "Sınav programı başarıyla oluşturuldu.", schedule_id
        except Exception as e:
            return False, f"Sınav programı oluşturulamadı: {str(e)}", None
    
    def create_multi_classroom(
        self,
        course_id: int,
        classroom_ids: List[int],
        exam_date: date,
        start_time: time,
        end_time: time,
        exam_type: str = "final",
        notes: str = None
    ) -> Tuple[bool, str, Optional[int]]:
        if not course_id:
            return False, "Ders seçimi gereklidir.", None
        
        if not classroom_ids or len(classroom_ids) == 0:
            return False, "En az bir derslik seçilmelidir.", None
        
        if start_time >= end_time:
            return False, "Bitiş saati başlangıç saatinden sonra olmalıdır.", None
        
        is_valid, error_message = self.validate_multi_classroom_exam(
            course_id=course_id,
            classroom_ids=classroom_ids,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time,
            exam_type=exam_type,
            exclude_id=None
        )
        
        if not is_valid:
            return False, error_message, None
        
        classroom_names = []
        for cid in classroom_ids:
            classroom = self.classroom_repo.get_by_id(cid)
            if classroom:
                classroom_names.append(classroom.name)
        
        combined_name = ", ".join(classroom_names)
        primary_classroom_id = classroom_ids[0]
        
        if len(classroom_ids) > 1:
            combined_notes = f"Birleşik derslikler: {combined_name}"
            if notes:
                combined_notes = f"{combined_notes}\n{notes.strip()}"
        else:
            combined_notes = notes.strip() if notes else None
        
        try:
            exam_schedule = ExamSchedule(
                course_id=course_id,
                classroom_id=primary_classroom_id,
                exam_date=exam_date,
                start_time=start_time,
                end_time=end_time,
                exam_type=exam_type,
                status="planned",
                notes=combined_notes
            )
            
            primary_id = self.repository.create(exam_schedule)
            
            for i, classroom_id in enumerate(classroom_ids[1:], start=2):
                additional_notes = f"Birleşik sınav ({i}/{len(classroom_ids)}) - Ana derslik: {classroom_names[0]}"
                if notes:
                    additional_notes = f"{additional_notes}\n{notes.strip()}"
                
                additional_exam = ExamSchedule(
                    course_id=course_id,
                    classroom_id=classroom_id,
                    exam_date=exam_date,
                    start_time=start_time,
                    end_time=end_time,
                    exam_type=exam_type,
                    status="planned",
                    notes=additional_notes
                )
                self.repository.create(additional_exam)
            
            self.clear_student_cache()
            
            if len(classroom_ids) > 1:
                return True, f"Sınav programı {len(classroom_ids)} derslikte başarıyla oluşturuldu.", primary_id
            else:
                return True, "Sınav programı başarıyla oluşturuldu.", primary_id
                
        except Exception as e:
            return False, f"Sınav programı oluşturulamadı: {str(e)}", None
    
    def update(self, schedule_id: int, course_id: int, classroom_id: int,
               exam_date: date, start_time: time, end_time: time,
               exam_type: str, status: str, notes: str = None) -> Tuple[bool, str]:
        exam_schedule = self.repository.get_by_id(schedule_id)
        if not exam_schedule:
            return False, "Sınav programı bulunamadı."
        
        if start_time >= end_time:
            return False, "Bitiş saati başlangıç saatinden sonra olmalıdır."
        
        if status != 'cancelled':
            is_valid, error_message = self.validate_exam_constraints(
                course_id=course_id,
                classroom_id=classroom_id,
                exam_date=exam_date,
                start_time=start_time,
                end_time=end_time,
                exam_type=exam_type,
                exclude_id=schedule_id
            )
            
            if not is_valid:
                return False, error_message
        
        exam_schedule.course_id = course_id
        exam_schedule.classroom_id = classroom_id
        exam_schedule.exam_date = exam_date
        exam_schedule.start_time = start_time
        exam_schedule.end_time = end_time
        exam_schedule.exam_type = exam_type
        exam_schedule.status = status
        exam_schedule.notes = notes.strip() if notes else None
        
        if self.repository.update(exam_schedule):
            self.clear_student_cache()
            return True, "Sınav programı başarıyla güncellendi."
        return False, "Sınav programı güncellenemedi."
    
    def delete(self, schedule_id: int) -> Tuple[bool, str]:
        if self.repository.delete(schedule_id):
            self.clear_student_cache()
            return True, "Sınav programı başarıyla silindi."
        return False, "Sınav programı silinemedi."
    
    def update_status(self, schedule_id: int, status: str) -> Tuple[bool, str]:
        if self.repository.update_status(schedule_id, status):
            return True, f"Sınav durumu '{status}' olarak güncellendi."
        return False, "Durum güncellenemedi."
    
    def get_exam_types(self) -> List[dict]:
        return [
            {"value": "midterm", "label": "Vize"},
            {"value": "final", "label": "Final"},
            {"value": "makeup", "label": "Bütünleme"},
            {"value": "quiz", "label": "Quiz"}
        ]
    
    def get_count(self) -> int:
        return self.repository.count()
    
    def get_by_status(self, status: str) -> List[ExamSchedule]:
        return self.repository.get_by_status(status)
    
    def check_all_constraints(
        self, 
        course_id: int, 
        classroom_id: int, 
        exam_date: date,
        start_time: time, 
        end_time: time, 
        exam_type: str = "final",
        exclude_id: int = None
    ) -> dict:
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'course_info': None,
            'classroom_info': None
        }
        
        course = self.course_repo.get_by_id(course_id)
        if not course:
            result['valid'] = False
            result['errors'].append("Ders bulunamadı.")
            return result
        
        result['course_info'] = {
            'code': course.code,
            'name': course.name,
            'student_count': course.student_count,
            'exam_duration': course.exam_duration,
            'year': course.year
        }
        
        classroom = self.classroom_repo.get_by_id(classroom_id)
        if not classroom:
            result['valid'] = False
            result['errors'].append("Derslik bulunamadı.")
            return result
        
        result['classroom_info'] = {
            'name': classroom.name,
            'capacity': classroom.capacity,
            'is_suitable': getattr(classroom, 'is_suitable', True)
        }
        
        start_time_str = start_time.strftime('%H:%M') if isinstance(start_time, time) else str(start_time)[:5]
        end_time_str = end_time.strftime('%H:%M') if isinstance(end_time, time) else str(end_time)[:5]
        
        is_valid, error_message = self.validate_exam_constraints(
            course_id=course_id,
            classroom_id=classroom_id,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time,
            exam_type=exam_type,
            exclude_id=exclude_id
        )
        
        if not is_valid:
            result['valid'] = False
            result['errors'].append(error_message)
        
        if course.student_count and classroom.capacity:
            usage_percent = (course.student_count / classroom.capacity) * 100
            if usage_percent > 80:
                result['warnings'].append(f"Derslik kapasitesi %{usage_percent:.0f} oranında dolacak.")
        
        return result
