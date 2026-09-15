import unittest
from app import create_app
from app.services.timetable_service import TimetableService

class TestLibrarySlot(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_1_library_slot_validation_default_subject(self):
        """Test Library slot without teacher and without subject defaults subject to 'Library / Reading Time'."""
        entry = {
            'day': 'Monday',
            'type': 'Library',
            'subject': '',
            'teacher': '',
            'start': '10:00 AM',
            'end': '11:00 AM'
        }
        valid, errs = TimetableService.validate_timetable_entry(entry)
        self.assertTrue(valid, f"Library slot should be valid without teacher/subject, got errors: {errs}")
        self.assertEqual(entry.get('subject'), 'Library / Reading Time')

    def test_2_library_slot_validation_custom_subject(self):
        """Test Library slot with custom subject and optional teacher."""
        entry = {
            'day': 'Monday',
            'type': 'Library',
            'subject': 'Digital Library & Research',
            'teacher': 'Mr. Incharge',
            'start': '11:00 AM',
            'end': '12:00 PM'
        }
        valid, errs = TimetableService.validate_timetable_entry(entry)
        self.assertTrue(valid, f"Custom Library slot should be valid, got errors: {errs}")
        self.assertEqual(entry.get('subject'), 'Digital Library & Research')

    def test_3_existing_lecture_lab_validation_unaffected(self):
        """Test that Lecture & Lab validation rules are unaffected."""
        # Lecture requires teacher
        lec_invalid = {
            'day': 'Monday',
            'type': 'Lecture',
            'subject': 'DBMS',
            'teacher': '',
            'start': '09:00 AM',
            'end': '10:00 AM'
        }
        valid_lec, errs_lec = TimetableService.validate_timetable_entry(lec_invalid)
        self.assertFalse(valid_lec)
        self.assertIn('teacher', errs_lec)

        # Lab requires 2 hours
        lab_invalid = {
            'day': 'Monday',
            'type': 'Lab',
            'subject': 'Python Lab',
            'teacher': 'Mr. Tarun',
            'start': '09:00 AM',
            'end': '10:00 AM'
        }
        valid_lab, errs_lab = TimetableService.validate_timetable_entry(lab_invalid)
        self.assertFalse(valid_lab)
        self.assertIn('end', errs_lab)

    def test_4_publish_and_retrieve_library_slot(self):
        """Test publishing timetable with Library slot and checking weekly schedule."""
        course = 'B.Tech CS'
        department = 'Computer Science & Technology'
        year = '3rd Year'
        section = 'Section A'

        weekly_schedule = {
            'Monday': [
                {'id': 'e1', 'subject': 'Data Structures', 'teacher': 'Dr. Sharma', 'type': 'Lecture', 'start': '09:00 AM', 'end': '10:00 AM'},
                {'id': 'e2', 'subject': 'Library / Reading Time', 'teacher': '', 'type': 'Library', 'start': '10:00 AM', 'end': '11:00 AM'}
            ],
            'Tuesday': [], 'Wednesday': [], 'Thursday': [], 'Friday': []
        }

        pub = TimetableService.publish_timetable(course, department, year, section, weekly_schedule)
        self.assertEqual(pub.get('status'), 'published')

        # Retrieve timetable
        tt = TimetableService.get_class_timetable(course, department, year, section)
        monday_slots = tt.get('weekly_schedule', {}).get('Monday', [])
        self.assertEqual(len(monday_slots), 2)
        lib_slot = monday_slots[1]
        self.assertEqual(lib_slot['type'], 'Library')
        self.assertEqual(lib_slot['subject'], 'Library / Reading Time')

if __name__ == '__main__':
    unittest.main()
