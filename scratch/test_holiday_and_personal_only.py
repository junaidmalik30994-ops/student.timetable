import unittest
from app import create_app
from app.services.auth_service import AuthService
from app.services.timetable_service import TimetableService
from app.utils.db import get_collection

class TestHolidayAndPersonalOnly(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_1_normal_student_registration_1st_year_a(self):
        # Case 1: Year = 1st Year, Section = Section A -> Normal student
        students_col = get_collection('students')
        students_col.delete_many({'email': 'student_1sta@shobhituniversity.ac.in'})

        success, errs, student = AuthService.register_student(
            full_name='Normal Student 1',
            email='student_1sta@shobhituniversity.ac.in',
            roll_number='SUG20261STA',
            password='password123',
            confirm_password='password123',
            course='B.Tech CS',
            department='Computer Science & Technology',
            year='1st Year',
            section='Section A'
        )
        self.assertTrue(success, f"Registration failed with errors: {errs}")
        self.assertEqual(student['schedule_type'], 'college_and_personal')

    def test_2_normal_student_registration_3rd_year_b(self):
        # Case 2: Year = 3rd Year, Section = Section B -> Normal student
        students_col = get_collection('students')
        students_col.delete_many({'email': 'student_3rdb@shobhituniversity.ac.in'})

        success, errs, student = AuthService.register_student(
            full_name='Normal Student 2',
            email='student_3rdb@shobhituniversity.ac.in',
            roll_number='SUG20263RDB',
            password='password123',
            confirm_password='password123',
            course='B.Tech CS',
            department='Computer Science & Technology',
            year='3rd Year',
            section='Section B'
        )
        self.assertTrue(success, f"Registration failed with errors: {errs}")
        self.assertEqual(student['schedule_type'], 'college_and_personal')

    def test_3_personal_schedule_student_registration_other_other(self):
        # Case 3: Year = Other, Section = Other -> Personal Schedule Only student
        students_col = get_collection('students')
        students_col.delete_many({'email': 'personal_user@shobhituniversity.ac.in'})

        success, errs, student = AuthService.register_student(
            full_name='Personal Schedule User',
            email='personal_user@shobhituniversity.ac.in',
            roll_number='SUG2026PER1',
            password='password123',
            confirm_password='password123',
            course='B.Tech CS',
            department='Computer Science & Technology',
            year='Other',
            section='Other'
        )
        self.assertTrue(success, f"Registration failed with errors: {errs}")
        self.assertEqual(student['schedule_type'], 'personal_only')

        # Check dashboard data payload for personal_only student
        dash_data = TimetableService.get_today_dashboard_data(student['id'])
        self.assertEqual(dash_data['schedule_type'], 'personal_only')
        self.assertEqual(dash_data['overview']['total_lectures'], 0)
        self.assertEqual(dash_data['current_activity']['title'], 'Personal Schedule Mode')

    def test_4_mismatched_other_year_normal_section(self):
        # Case 4: Year = Other, Section = Section A -> Validation error
        success, errs, student = AuthService.register_student(
            full_name='Test Mismatch 1',
            email='mismatch1@shobhituniversity.ac.in',
            roll_number='SUG2026MIS1',
            password='password123',
            confirm_password='password123',
            course='B.Tech CS',
            department='Computer Science & Technology',
            year='Other',
            section='Section A'
        )
        self.assertFalse(success)
        self.assertIn('section', errs)
        self.assertEqual(errs['section'], 'For Personal Schedule mode, please select Other for both Year and Section.')

    def test_5_mismatched_normal_year_other_section(self):
        # Case 5: Year = 2nd Year, Section = Other -> Validation error
        success, errs, student = AuthService.register_student(
            full_name='Test Mismatch 2',
            email='mismatch2@shobhituniversity.ac.in',
            roll_number='SUG2026MIS2',
            password='password123',
            confirm_password='password123',
            course='B.Tech CS',
            department='Computer Science & Technology',
            year='2nd Year',
            section='Other'
        )
        self.assertFalse(success)
        self.assertIn('section', errs)
        self.assertEqual(errs['section'], 'For Personal Schedule mode, please select Other for both Year and Section.')

    def test_6_saturday_college_holiday_validation(self):
        # Case 6 & 9: Admin tries to add Saturday timetable slot -> Rejected
        entry = {
            'day': 'Saturday',
            'type': 'Lecture',
            'subject': 'Weekend Class',
            'teacher': 'Mr. Test',
            'start': '09:00 AM',
            'end': '10:00 AM'
        }
        valid, errs = TimetableService.validate_timetable_entry(entry)
        self.assertFalse(valid)
        self.assertIn('day', errs)
        self.assertEqual(errs['day'], 'Saturday is a college holiday. Timetable slots cannot be added.')

    def test_7_monday_to_friday_timetable_validation(self):
        # Case 7: Admin adds Monday timetable slot -> Valid
        entry = {
            'day': 'Monday',
            'type': 'Lecture',
            'subject': 'Operating Systems',
            'teacher': 'Prof. Ankit',
            'start': '09:00 AM',
            'end': '10:00 AM'
        }
        valid, errs = TimetableService.validate_timetable_entry(entry)
        self.assertTrue(valid, f"Expected valid Monday slot, got: {errs}")

    def test_8_weekly_timetable_structure_has_no_saturday(self):
        weekly = TimetableService.get_weekly_timetable()
        self.assertIn('Monday', weekly)
        self.assertIn('Friday', weekly)
        self.assertNotIn('Saturday', weekly)
        self.assertNotIn('Sunday', weekly)

if __name__ == '__main__':
    unittest.main()
