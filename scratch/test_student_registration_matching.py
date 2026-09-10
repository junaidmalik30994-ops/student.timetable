import unittest
from app import create_app
from app.services.auth_service import AuthService
from app.services.timetable_service import TimetableService
from app.utils.db import get_collection

class TestStudentRegistrationMatching(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_student_registration_with_class_fields(self):
        students_col = get_collection('students')
        students_col.delete_many({'email': 'test_student_4th@shobhituniversity.ac.in'})

        success, errs, student = AuthService.register_student(
            full_name='Aman Verma',
            email='test_student_4th@shobhituniversity.ac.in',
            roll_number='SUG2026CS401',
            password='password123',
            confirm_password='password123',
            course='B.Tech CS',
            department='Computer Science & Technology',
            year='4th Year',
            section='Section A'
        )

        self.assertTrue(success, f"Expected successful registration, got errors: {errs}")
        self.assertEqual(student['course'], 'B.Tech CS')
        self.assertEqual(student['department'], 'Computer Science & Technology')
        self.assertEqual(student['year'], '4th Year')
        self.assertEqual(student['section'], 'Section A')

        # Verify document stored in MongoDB contains all fields
        saved = students_col.find_one({'email': 'test_student_4th@shobhituniversity.ac.in'})
        self.assertIsNotNone(saved)
        self.assertEqual(saved['full_name'], 'Aman Verma')
        self.assertEqual(saved['roll_number'], 'SUG2026CS401')
        self.assertEqual(saved['course'], 'B.Tech CS')
        self.assertEqual(saved['department'], 'Computer Science & Technology')
        self.assertEqual(saved['year'], '4th Year')
        self.assertEqual(saved['section'], 'Section A')

    def test_timetable_matching_by_exact_class(self):
        # 1. Publish timetable for 4th Year Section A
        schedule_4th = {
            'Monday': [{'id': 'm1', 'subject': 'Cloud Computing', 'teacher': 'Prof Kapoor', 'type': 'Lecture', 'start': '09:00 AM', 'end': '10:00 AM'}],
            'Tuesday': [], 'Wednesday': [], 'Thursday': [], 'Friday': [], 'Saturday': []
        }
        TimetableService.publish_timetable(
            course='B.Tech CS',
            department='Computer Science & Technology',
            year='4th Year',
            section='Section A',
            weekly_schedule=schedule_4th
        )

        # 2. Register 4th Year Section A student
        students_col = get_collection('students')
        students_col.delete_many({'email': 'aman_4th@shobhituniversity.ac.in'})
        _, _, st_4th = AuthService.register_student(
            full_name='Aman 4th Year',
            email='aman_4th@shobhituniversity.ac.in',
            roll_number='SUG4TH001',
            password='password123',
            confirm_password='password123',
            course='B.Tech CS',
            department='Computer Science & Technology',
            year='4th Year',
            section='Section A'
        )

        # 3. Register 2nd Year Section B student (No timetable published)
        students_col.delete_many({'email': 'priya_2nd@shobhituniversity.ac.in'})
        _, _, st_2nd = AuthService.register_student(
            full_name='Priya 2nd Year',
            email='priya_2nd@shobhituniversity.ac.in',
            roll_number='SUG2ND001',
            password='password123',
            confirm_password='password123',
            course='BCA',
            department='Computer Science & Technology',
            year='2nd Year',
            section='Section B'
        )

        # 4. Fetch timetable for 4th Year student -> Must get 4th Year timetable
        weekly_4th = TimetableService.get_weekly_timetable(student_id=st_4th['id'])
        self.assertEqual(len(weekly_4th['Monday']), 1)
        self.assertEqual(weekly_4th['Monday'][0]['subject'], 'Cloud Computing')

        # 5. Fetch timetable for 2nd Year student -> Must get empty schedule
        weekly_2nd = TimetableService.get_weekly_timetable(student_id=st_2nd['id'])
        self.assertEqual(len(weekly_2nd['Monday']), 0)

if __name__ == '__main__':
    unittest.main()
