import unittest
from datetime import datetime
from app import create_app
from app.services.timetable_service import TimetableService

class TestPersonalTaskAMPM(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_ampm_time_parsing(self):
        # 11:00 AM -> 660 mins
        self.assertEqual(TimetableService.parse_time_mins('11:00 AM'), 660)
        # 1:00 PM -> 780 mins
        self.assertEqual(TimetableService.parse_time_mins('1:00 PM'), 780)
        # 05:00 PM -> 1020 mins
        self.assertEqual(TimetableService.parse_time_mins('05:00 PM'), 1020)
        # 06:00 PM -> 1080 mins
        self.assertEqual(TimetableService.parse_time_mins('06:00 PM'), 1080)
        # 12:00 AM -> 0 mins
        self.assertEqual(TimetableService.parse_time_mins('12:00 AM'), 0)
        # 12:00 PM -> 720 mins
        self.assertEqual(TimetableService.parse_time_mins('12:00 PM'), 720)

    def test_ampm_time_formatting(self):
        self.assertEqual(TimetableService.format_time_12h('17:00'), '05:00 PM')
        self.assertEqual(TimetableService.format_time_12h('18:00'), '06:00 PM')
        self.assertEqual(TimetableService.format_time_12h('11:00 AM'), '11:00 AM')
        self.assertEqual(TimetableService.format_time_12h('1:00 PM'), '01:00 PM')

    def test_task_time_validation_cases(self):
        # Requirement 7:
        # 11:00 AM -> 1:00 PM = Valid
        s1 = TimetableService.parse_time_mins('11:00 AM')
        e1 = TimetableService.parse_time_mins('1:00 PM')
        self.assertTrue(e1 > s1, "11:00 AM -> 1:00 PM should be valid (1:00 PM after 11:00 AM)")

        # 5:00 PM -> 6:00 PM = Valid
        s2 = TimetableService.parse_time_mins('5:00 PM')
        e2 = TimetableService.parse_time_mins('6:00 PM')
        self.assertTrue(e2 > s2, "5:00 PM -> 6:00 PM should be valid")

        # 6:00 PM -> 5:00 PM = Invalid
        s3 = TimetableService.parse_time_mins('6:00 PM')
        e3 = TimetableService.parse_time_mins('5:00 PM')
        self.assertFalse(e3 > s3, "6:00 PM -> 5:00 PM should be invalid")

        # 5:00 PM -> 5:00 PM = Invalid
        s4 = TimetableService.parse_time_mins('5:00 PM')
        e4 = TimetableService.parse_time_mins('5:00 PM')
        self.assertFalse(e4 > s4, "5:00 PM -> 5:00 PM should be invalid")

    def test_api_validation(self):
        with self.client.session_transaction() as sess:
            sess['student_id'] = 'test_student_123'
            sess['student_name'] = 'Test Student'

        # Test valid creation
        res = self.client.post('/api/tasks', json={
            'title': 'Test Study Task',
            'date': '2026-08-28',
            'start': '11:00 AM',
            'end': '01:00 PM'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        task_id = data['task']['id']

        # Test invalid creation (6:00 PM -> 5:00 PM)
        res_invalid = self.client.post('/api/tasks', json={
            'title': 'Invalid Task',
            'date': '2026-08-28',
            'start': '06:00 PM',
            'end': '05:00 PM'
        })
        self.assertEqual(res_invalid.status_code, 400)
        data_inv = res_invalid.get_json()
        self.assertFalse(data_inv.get('success'))
        self.assertEqual(data_inv.get('message'), 'End time must be after Start time.')

        # Clean up created task
        self.client.delete(f'/api/tasks/{task_id}')

if __name__ == '__main__':
    unittest.main()
