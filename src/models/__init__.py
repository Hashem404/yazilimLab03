"""
Model modülü
Veritabanı entity sınıflarını içerir
"""

from .faculty import Faculty
from .department import Department
from .classroom import Classroom, CLASSROOM_TYPE_MAP, CLASSROOM_TYPES
from .lecturer import Lecturer, DEFAULT_AVAILABLE_DAYS, ALL_WEEKDAYS
from .course import (
    Course,
    COURSE_TYPES,
    EXAM_TYPES,
    EXAM_DURATION_OPTIONS,
    REQUIRED_ROOM_TYPE_OPTIONS,
    REQUIRED_ROOM_TYPE_MAP,
    COURSE_TYPE_MAP,
    EXAM_TYPE_MAP
)
from .exam_schedule import ExamSchedule
from .user import User
from .student import Student, StudentCourse
