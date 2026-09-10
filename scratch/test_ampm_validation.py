import unittest
from app import create_app
from app.services.timetable_service import TimetableService

class TestAMPMTimeValidation(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True

    def test_ampm_parsing(self):
        self.assertEqual(TimetableService.parse_time_mins('9:00 AM'), 540)
        self.assertEqual(TimetableService.parse_time_mins('10:00 AM'), 600)
        self.assertEqual(TimetableService.parse_time_mins('11:00 AM'), 660)
        self.assertEqual(TimetableService.parse_time_mins('12:00 PM'), 720)
        self.assertEqual(TimetableService.parse_time_mins('1:00 PM'), 780)
        self.assertEqual(TimetableService.parse_time_mins('2:00 PM'), 840)
        self.assertEqual(TimetableService.parse_time_mins('3:00 PM'), 900)
        self.assertEqual(TimetableService.parse_time_mins('12:00 AM'), 0)

    def test_user_cases(self):
        # Case 1: 9:00 AM -> 10:00 AM (Lecture) = Valid
        valid1, errs1 = TimetableService.validate_timetable_entry({
            'subject': 'Mathematics',
            'teacher': 'Dr. Sharma',
            'type': 'Lecture',
            'start': '9:00 AM',
            'end': '10:00 AM'
        })
        self.assertTrue(valid1, f"Expected 9:00 AM -> 10:00 AM to be valid, got errors: {errs1}")

        # Case 2: 9:00 AM -> 11:00 AM (Lab, 2 hours) = Valid
        valid2, errs2 = TimetableService.validate_timetable_entry({
            'subject': 'Python Lab',
            'teacher': 'Mr. Tarun Saini',
            'type': 'Lab',
            'start': '9:00 AM',
            'end': '11:00 AM'
        })
        self.assertTrue(valid2, f"Expected 9:00 AM -> 11:00 AM (2h Lab) to be valid, got errors: {errs2}")

        # Case 3: 11:00 AM -> 1:00 PM (Lab, 2 hours) = Valid
        valid3, errs3 = TimetableService.validate_timetable_entry({
            'subject': 'Database Lab',
            'teacher': 'Mr. Tarun Saini',
            'type': 'Lab',
            'start': '11:00 AM',
            'end': '1:00 PM'
        })
        self.assertTrue(valid3, f"Expected 11:00 AM -> 1:00 PM (2h Lab) to be valid, got errors: {errs3}")

        # Case 4: 1:00 PM -> 3:00 PM (Lab, 2 hours) = Valid
        valid4, errs4 = TimetableService.validate_timetable_entry({
            'subject': 'Web Tech Lab',
            'teacher': 'Mr. Tarun Saini',
            'type': 'Lab',
            'start': '1:00 PM',
            'end': '3:00 PM'
        })
        self.assertTrue(valid4, f"Expected 1:00 PM -> 3:00 PM (2h Lab) to be valid, got errors: {errs4}")

        # Case 5: 3:00 PM -> 2:00 PM = Invalid
        valid5, errs5 = TimetableService.validate_timetable_entry({
            'subject': 'Physics',
            'teacher': 'Prof Verma',
            'type': 'Lecture',
            'start': '3:00 PM',
            'end': '2:00 PM'
        })
        self.assertFalse(valid5, "Expected 3:00 PM -> 2:00 PM to be invalid")
        self.assertIn('end', errs5)

if __name__ == '__main__':
    unittest.main()
