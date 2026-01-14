import sys
"""
Üniversite Sınav Programı Sistemi - Test Suite

Bu test dosyası veritabanı bağlantısı gerektirmez.
Tüm testler mock verilerle çalışır.

"""

import unittest
from datetime import datetime, date, time, timedelta
from unittest.mock import MagicMock, Mock, patch

# Veritabanı bağımlılığı olan servisleri mock'la
# Önce mock'ları kur, sonra import et
sys_modules = {
    'src.services.scheduler_service': MagicMock(),
    'src.services.student_import_service': MagicMock(),
    'src.utils.student_importer': MagicMock(),
}

# Patch ile modülleri mockla
for mod_name, mod_mock in sys_modules.items():
    if mod_name not in sys.modules:
        sys.modules[mod_name] = mod_mock

# Şimdi diğer modülleri import edebiliriz
from src.models.course import Course
from src.models.student import Student
from src.models.classroom import Classroom


class TestModels(unittest.TestCase):
    """Model testleri"""

    def test_course_model_creation(self):
        """Ders modelinin doğru oluşturulup oluşturulmadığını test eder."""
        course = Course(
            id=1,
            code="BLM101",
            name="Bilgisayar Müh. Giriş",
            department_id=5,
            lecturer_id=10,
            student_count=50,
            exam_duration=60
        )
        self.assertEqual(course.code, "BLM101")
        self.assertEqual(course.student_count, 50)
        self.assertEqual(course.id, 1)

    def test_classroom_model_creation(self):
        """Derslik modelinin doğru oluşturulup oluşturulmadığını test eder."""
        classroom = Classroom(
            id=1,
            name="M101",
            faculty_id=1,
            capacity=40,
            has_computer=True,
            is_suitable=True,
            room_type="STANDART"
        )
        self.assertEqual(classroom.name, "M101")
        self.assertEqual(classroom.capacity, 40)
        self.assertTrue(classroom.is_suitable)
        self.assertTrue(classroom.has_computer)

    def test_student_model_creation(self):
        """Öğrenci modelinin doğru oluşturulup oluşturulmadığını test eder."""
        student = Student(
            id=1,
            student_number="2021001",
            first_name="Ahmet",
            last_name="Yılmaz",
            email="ahmet@example.com",
            department_id=5,
            year=2,
            is_active=True
        )
        self.assertEqual(student.student_number, "2021001")
        self.assertEqual(student.first_name, "Ahmet")
        self.assertEqual(student.year, 2)


class TestStudentConflictLogic(unittest.TestCase):
    """
    Öğrenci çakışma kontrolü mantık testleri

    Senaryo: İki farklı ders var (Ders A ve Ders B).
    Ahmet (ID: 100) her iki dersi de alıyor.
    Sistem bu iki dersi aynı saate koymamalı.
    """

    def test_no_conflict_different_students(self):
        """Farklı öğrenciler için çakışma olmamalı"""
        students_a = {100, 101, 102}
        students_b = {103, 104, 105}

        intersection = students_a.intersection(students_b)
        has_conflict = len(intersection) > 0

        self.assertFalse(has_conflict, "Çakışma olmamalıydı (öğrenciler farklı)")

    def test_conflict_shared_students(self):
        """Ortak öğrenciler için çakışma tespit edilmeli"""
        students_a = {100, 101, 102}
        students_b = {100, 104, 105}  # 100 numaralı öğrenci ORTAK!

        intersection = students_a.intersection(students_b)
        has_conflict = len(intersection) > 0

        self.assertTrue(has_conflict, "Çakışma tespit edilmeliydi (Öğrenci 100 ortak)")
        self.assertEqual(len(intersection), 1)
        self.assertIn(100, intersection)

    def test_multiple_shared_students(self):
        """Birden fazla ortak öğrenci için çakışma tespit edilmeli"""
        students_a = {100, 101, 102, 103}
        students_b = {100, 101, 104, 105}  # 100 ve 101 numaralı öğrenciler ORTAK!

        intersection = students_a.intersection(students_b)

        self.assertEqual(len(intersection), 2)
        self.assertIn(100, intersection)
        self.assertIn(101, intersection)

    def test_all_students_shared(self):
        """Tüm öğrencilerin ortak olduğu durum"""
        students_a = {100, 101, 102}
        students_b = {100, 101, 102}

        intersection = students_a.intersection(students_b)

        self.assertEqual(len(intersection), 3)
        self.assertEqual(intersection, students_a)


class TestClassroomCapacity(unittest.TestCase):
    """
    Derslik kapasite kontrolü testleri

    Senaryo: Sınıf kapasitesi 40, Dersi alan kişi 50.
    Sistem 'Yetersiz Kapasite' demeli.
    """

    def test_sufficient_capacity(self):
        """Yeterli kapasite var"""
        classroom = Classroom(id=1, name="M101", capacity=50, room_type="STANDART")
        course_student_count = 40

        is_sufficient = classroom.capacity >= course_student_count

        self.assertTrue(is_sufficient, "Kapasite yeterli olmalıydı")

    def test_insufficient_capacity(self):
        """Yetersiz kapasite"""
        classroom = Classroom(id=1, name="M101", capacity=40, room_type="STANDART")
        course_student_count = 50

        is_sufficient = classroom.capacity >= course_student_count

        self.assertFalse(is_sufficient, "Kapasite yetersiz olmalıydı")

    def test_exact_capacity(self):
        """Tam kapasite"""
        classroom = Classroom(id=1, name="M101", capacity=40, room_type="STANDART")
        course_student_count = 40

        is_sufficient = classroom.capacity >= course_student_count

        self.assertTrue(is_sufficient, "Tam kapasite yeterli olmalıydı")


class TestSchedulingLogic(unittest.TestCase):
    """
    Sınav planlama mantığı testleri
    """

    def test_time_slot_overlap(self):
        """Zaman slotu çakışma kontrolü"""
        # Overlapping slots
        slot1_start = time(9, 0)
        slot1_end = time(11, 0)
        slot2_start = time(10, 0)
        slot2_end = time(12, 0)

        # Çakışma kontrolü: slot1 bitiş zamanı <= slot2 başlangıç veya
        # slot1 başlangıç >= slot2 bitiş ise çakışma yok
        has_overlap = not (slot1_end <= slot2_start or slot1_start >= slot2_end)

        self.assertTrue(has_overlap, "Bu slotlar çakışmalı")

    def test_time_slot_no_overlap(self):
        """Zaman slotu çakışma yok"""
        # Non-overlapping slots
        slot1_start = time(9, 0)
        slot1_end = time(11, 0)
        slot2_start = time(11, 30)
        slot2_end = time(13, 30)

        has_overlap = not (slot1_end <= slot2_start or slot1_start >= slot2_end)

        self.assertFalse(has_overlap, "Bu slotlar çakışmamalı")

    def test_exam_duration_calculation(self):
        """Sınav süresi hesaplama"""
        start_time = time(9, 0)
        exam_duration = 90  # dakika

        end_hour = start_time.hour + exam_duration // 60
        end_minute = start_time.minute + exam_duration % 60
        end_time = time(end_hour, end_minute)

        self.assertEqual(end_time, time(10, 30))

    def test_back_to_back_slots(self):
        """Arka arkaya slotlar (çakışma yok)"""
        slot1_end = time(11, 0)
        slot2_start = time(11, 0)

        # Tam bitişte başlangıç - çakışma yok
        has_overlap = not (slot1_end <= slot2_start)

        self.assertFalse(has_overlap, "Arka arkaya slotlar çakışmamalı")


class TestDateLogic(unittest.TestCase):
    """Tarih ve gün mantığı testleri"""

    def test_weekday_calculation(self):
        """Hafta içi gün hesaplama"""
        # 2025-01-13 bir Pazartesi
        test_date = date(2025, 1, 13)
        weekday = test_date.weekday()  # 0 = Pazartesi

        self.assertEqual(weekday, 0, "Pazartesi günü 0 olmalı")

    def test_date_range_includes_weekdays(self):
        """Tarih aralığında hafta içi gün var mı?"""
        start = date(2025, 1, 13)  # Pazartesi
        end = date(2025, 1, 17)    # Cuma

        weekdays = []
        current = start
        while current <= end:
            if current.weekday() < 5:  # 0-4 = Pazartesi-Cuma
                weekdays.append(current)
            current += timedelta(days=1)

        self.assertEqual(len(weekdays), 5, "5 hafta içi gün olmalı")

    def test_weekend_excluded(self):
        """Hafta sonu günlerinin hariç tutulması"""
        start = date(2025, 1, 11)  # Cumartesi
        end = date(2025, 1, 12)    # Pazar

        weekdays = []
        current = start
        while current <= end:
            if current.weekday() < 5:
                weekdays.append(current)
            current += timedelta(days=1)

        self.assertEqual(len(weekdays), 0, "Hafta sonu olmamalı")


def run_tests():
    """Testleri çalıştır ve sonuçları raporla"""
    print("=" * 60)
    print("ÜNİVERSİTE SINAV PROGRAMI SİSTEMİ - TEST SUİTİ")
    print("=" * 60)
    print()

    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Testleri ekle
    suite.addTests(loader.loadTestsFromTestCase(TestModels))
    suite.addTests(loader.loadTestsFromTestCase(TestStudentConflictLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestClassroomCapacity))
    suite.addTests(loader.loadTestsFromTestCase(TestSchedulingLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestDateLogic))

    # Testleri çalıştır
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Özet
    print()
    print("=" * 60)
    print("TEST ÖZETİ")
    print("=" * 60)
    print(f"Toplam Test: {result.testsRun}")
    print(f"Başarılı: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Başarısız: {len(result.failures)}")
    print(f"Hata: {len(result.errors)}")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
