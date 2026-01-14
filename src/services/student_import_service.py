"""
Öğrenci İçe Aktarma Servisi

Excel dosyalarından öğrenci listelerini okuyup veritabanına kaydeden servistir.
Kullanım:
    from src.services.student_import_service import StudentImportService
    
    service = StudentImportService()
    result = service.import_from_excel("exceller/SınıfListesi[BLM111].xls", course_id=1)
"""

from typing import Dict, List, Optional
from src.utils.student_importer import StudentImporter, ImportResult
from src.repositories.course_repository import CourseRepository
from src.repositories.department_repository import DepartmentRepository


class StudentImportService:

    
    def __init__(self):
        self.importer = StudentImporter()
        self.course_repo = CourseRepository()
        self.department_repo = DepartmentRepository()
    
    def import_from_excel(
        self,
        file_path: str,
        course_id: Optional[int] = None,
        course_code: Optional[str] = None,
        department_id: Optional[int] = None,
        semester: Optional[str] = None,
        year: Optional[int] = None
    ) -> ImportResult:
        return self.importer.import_from_excel(
            file_path=file_path,
            course_id=course_id,
            course_code=course_code,
            department_id=department_id,
            semester=semester,
            year=year
        )
    
    def import_from_excel_directory(
        self,
        directory_path: str,
        semester: Optional[str] = None,
        department_id: Optional[int] = None
    ) -> Dict[str, ImportResult]:
        return self.importer.import_from_excel_directory(
            directory_path=directory_path,
            semester=semester,
            department_id=department_id
        )
    
    def get_import_summary(self, results: Dict[str, ImportResult]) -> Dict:
        total_files = len(results)
        successful_files = sum(1 for r in results.values() if r.success)
        total_students = sum(r.students_imported for r in results.values())
        total_student_courses = sum(r.student_courses_created for r in results.values())
        
        failed_files = [
            filename for filename, result in results.items() 
            if not result.success
        ]
        
        return {
            'total_files': total_files,
            'successful_files': successful_files,
            'failed_files': len(failed_files),
            'failed_file_list': failed_files,
            'total_students_imported': total_students,
            'total_student_courses_created': total_student_courses,
            'success_rate': round(successful_files / total_files * 100, 2) if total_files > 0 else 0
        }
    
    def get_available_courses_for_import(self) -> List[Dict]:
        courses = self.course_repo.get_all()
        return [
            {
                'id': c.id,
                'code': c.code,
                'name': c.name,
                'department_id': c.department_id,
                'department_name': c.department_name,
                'year': c.year,
                'student_count': c.student_count
            }
            for c in courses
        ]
    
    def validate_import_requirements(self, course_id: int) -> Dict[str, any]:
        course = self.course_repo.get_by_id(course_id)
        
        if not course:
            return {
                'valid': False,
                'reason': 'Ders bulunamadı'
            }
        
        if not course.has_exam:
            return {
                'valid': False,
                'reason': 'Bu dersin sınavı yok (has_exam=False)'
            }
        
        return {
            'valid': True,
            'course': {
                'id': course.id,
                'code': course.code,
                'name': course.name,
                'student_count': course.student_count
            }
        }
