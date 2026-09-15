import unittest
from app import create_app
from app.services.timetable_service import TimetableService
from app.utils.db import get_collection

class TestAdminTimetableValidation(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_1_valid_normal_subject_entry(self):
        entry = {
            'day': 'Monday',
            'type': 'Lecture',
            'subject': 'Data Structures',
            'teacher': 'Dr. Sharma',
            'start': '09:00 AM',
            'end': '10:00 AM'
        }
        valid, errs = TimetableService.validate_timetable_entry(entry)
        self.assertTrue(valid, f"Expected valid, got errors: {errs}")

    def test_2_missing_subject_name(self):
        entry = {
            'day': 'Monday',
            'type': 'Lecture',
            'subject': '',
            'teacher': 'Dr. Sharma',
            'start': '09:00 AM',
            'end': '10:00 AM'
        }
        valid, errs = TimetableService.validate_timetable_entry(entry)
        self.assertFalse(valid)
        self.assertIn('subject', errs)
        self.assertEqual(errs['subject'], 'Subject name is required.')

    def test_3_missing_teacher_name(self):
        entry = {
            'day': 'Monday',
            'type': 'Lecture',
            'subject': 'Data Structures',
            'teacher': '',
            'start': '09:00 AM',
            'end': '10:00 AM'
        }
        valid, errs = TimetableService.validate_timetable_entry(entry)
        self.assertFalse(valid)
        self.assertIn('teacher', errs)
        self.assertEqual(errs['teacher'], 'Teacher name is required.')

    def test_4_invalid_start_end_time(self):
        entry = {
            'day': 'Monday',
            'type': 'Lecture',
            'subject': 'Data Structures',
            'teacher': 'Dr. Sharma',
            'start': '10:00 AM',
            'end': '09:00 AM'
        }
        valid, errs = TimetableService.validate_timetable_entry(entry)
        self.assertFalse(valid)
        self.assertIn('end', errs)
        self.assertEqual(errs['end'], 'End time must be after start time.')

    def test_5_incorrect_duration_for_lab(self):
        entry = {
            'day': 'Monday',
            'type': 'Lab',
            'subject': 'Python Lab',
            'teacher': 'Mr. Tarun',
            'start': '09:00 AM',
            'end': '10:00 AM'  # Only 1 hour instead of 2
        }
        valid, errs = TimetableService.validate_timetable_entry(entry)
        self.assertFalse(valid)
        self.assertIn('end', errs)
        self.assertIn('Labs must be 2 hours', errs['end'])

    def test_6_valid_2_hour_lab(self):
        entry = {
            'day': 'Monday',
            'type': 'Lab',
            'subject': 'Python Lab',
            'teacher': 'Mr. Tarun',
            'start': '09:00 AM',
            'end': '11:00 AM'  # Exactly 2 hours
        }
        valid, errs = TimetableService.validate_timetable_entry(entry)
        self.assertTrue(valid, f"Expected valid 2-hour lab, got errors: {errs}")

    def test_7_publish_timetable_api(self):
        course = 'B.Tech CS'
        department = 'Computer Science & Technology'
        year = '3rd Year'
        section = 'Section A'

        weekly_schedule = {
            'Monday': [
                {'id': 'e1', 'subject': 'Database Systems', 'teacher': 'Dr. Gupta', 'type': 'Lecture', 'start': '09:00 AM', 'end': '10:00 AM'}
            ],
            'Tuesday': [], 'Wednesday': [], 'Thursday': [], 'Friday': [], 'Saturday': []
        }

        pub = TimetableService.publish_timetable(course, department, year, section, weekly_schedule)
        self.assertEqual(pub['status'], 'published')
        self.assertTrue(pub['is_active'])

if __name__ == '__main__':
    unittest.main()
