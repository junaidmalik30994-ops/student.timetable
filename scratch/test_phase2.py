import unittest
from datetime import datetime
from app import create_app
from app.services.timetable_service import TimetableService
from app.utils.db import get_collection

class TestPhase2Features(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_timetable_entry_validation(self):
        # 1. Missing subject
        valid, errs = TimetableService.validate_timetable_entry({
            'subject': '', 'teacher': 'Tarun Saini', 'type': 'Lecture', 'start': '09:00', 'end': '10:00'
        })
        self.assertFalse(valid)
        self.assertIn('subject', errs)

        # 2. Missing teacher for Lecture
        valid, errs = TimetableService.validate_timetable_entry({
            'subject': 'Python', 'teacher': '', 'type': 'Lecture', 'start': '09:00', 'end': '10:00'
        })
        self.assertFalse(valid)
        self.assertIn('teacher', errs)

        # 3. Lab duration not 2 hours
        valid, errs = TimetableService.validate_timetable_entry({
            'subject': 'Python Lab', 'teacher': 'Tarun Saini', 'type': 'Lab', 'start': '09:00', 'end': '10:00'
        })
        self.assertFalse(valid)
        self.assertIn('type', errs)

        # 4. Valid 2-hour Lab
        valid, errs = TimetableService.validate_timetable_entry({
            'subject': 'Python Lab', 'teacher': 'Tarun Saini', 'type': 'Lab', 'start': '09:00', 'end': '11:00'
        })
        self.assertTrue(valid)

        # 5. Overlap detection
        existing = [{'id': '1', 'subject': 'Math', 'teacher': 'Prof A', 'start': '09:00', 'end': '10:00'}]
        valid, errs = TimetableService.validate_timetable_entry({
            'subject': 'Physics', 'teacher': 'Prof B', 'type': 'Lecture', 'start': '09:30', 'end': '10:30'
        }, day_entries=existing)
        self.assertFalse(valid)
        self.assertIn('general', errs)

    def test_publish_and_student_timetable(self):
        course = 'B.Tech CS'
        department = 'Computer Science & Technology'
        year = '3rd Year'
        section = 'Section A'

        weekly_schedule = {
            'Monday': [
                {'id': 'm1', 'subject': 'Python Programming', 'teacher': 'Mr. Tarun Saini', 'type': 'Lecture', 'start': '09:00', 'end': '10:00'},
                {'id': 'm2', 'subject': 'Python Lab', 'teacher': 'Mr. Tarun Saini', 'type': 'Lab', 'start': '11:00', 'end': '13:00'}
            ],
            'Tuesday': [], 'Wednesday': [], 'Thursday': [], 'Friday': [], 'Saturday': []
        }

        # Publish timetable
        pub = TimetableService.publish_timetable(course, department, year, section, weekly_schedule)
        self.assertEqual(pub['status'], 'published')

        # Fetch weekly timetable for student
        weekly = TimetableService.get_weekly_timetable()
        self.assertIn('Monday', weekly)
        self.assertEqual(len(weekly['Monday']), 2)
        self.assertEqual(weekly['Monday'][0]['subject'], 'Python Programming')
        self.assertEqual(weekly['Monday'][1]['subject'], 'Python Lab')

    def test_personal_task_crud_and_dashboard(self):
        student_id = 'test_student_p2'
        tasks_col = get_collection('tasks')
        tasks_col.delete_many({'student_id': student_id})

        today_str = datetime.now().strftime('%Y-%m-%d')

        # 1. Add personal task
        task = TimetableService.add_personal_task(
            student_id=student_id,
            title='Prepare Assignment',
            date_str=today_str,
            start_time='16:00',
            end_time='17:00'
        )
        self.assertIsNotNone(task.get('id'))

        # 2. Fetch tasks
        tasks = TimetableService.get_student_tasks(student_id)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['title'], 'Prepare Assignment')

        # 3. Update task
        ok, updated = TimetableService.update_personal_task(
            student_id=student_id,
            task_id=task['id'],
            title='Prepare Python Assignment',
            date_str=today_str,
            start_time='16:30',
            end_time='17:30'
        )
        self.assertTrue(ok)
        self.assertEqual(updated['title'], 'Prepare Python Assignment')

        # 4. Check dashboard integration
        dash_data = TimetableService.get_today_dashboard_data(student_id)
        self.assertEqual(dash_data['overview']['total_tasks'], 1)

        # 5. Delete task
        deleted = TimetableService.delete_personal_task(student_id, task['id'])
        self.assertTrue(deleted)
        self.assertEqual(len(TimetableService.get_student_tasks(student_id)), 0)

if __name__ == '__main__':
    unittest.main()
