"""
Repository modülü
Veritabanı erişim katmanını içerir
"""

from .base_repository import BaseRepository
from .faculty_repository import FacultyRepository
from .department_repository import DepartmentRepository
from .classroom_repository import ClassroomRepository
from .lecturer_repository import LecturerRepository
from .course_repository import CourseRepository
from .exam_schedule_repository import ExamScheduleRepository
from .user_repository import UserRepository
from .student_repository import StudentRepository, StudentCourseRepository
