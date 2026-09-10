import unittest
from app import create_app
from app.services.timetable_service import TimetableService
from app.services.admin_service import AdminService
from app.utils.db import get_collection

class TestTimetableEmptyState(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_no_demo_data_in_dashboard(self):
        student_id = 'test_student_clean_123'
        
        # Clean tasks for this test student
        tasks_col = get_collection('tasks')
        tasks_col.delete_many({'student_id': student_id})

        # Fetch student tasks
        tasks = TimetableService.get_student_tasks(student_id)
        self.assertEqual(len(tasks), 0, "Student tasks should be empty initially (no auto-seeding)")

        # Fetch dashboard data
        dash_data = TimetableService.get_today_dashboard_data(student_id)
        
        # Verify Current Activity empty state
        self.assertEqual(dash_data['current_activity']['title'], 'No current lecture')
        
        # Verify Next Up empty state
        self.assertEqual(dash_data['next_up']['title'], 'No upcoming activity')
        
        # Verify lecture metrics are 0
        self.assertEqual(dash_data['overview']['total_lectures'], 0)
        self.assertEqual(dash_data['overview']['completed_lectures'], 0)
        self.assertEqual(dash_data['overview']['remaining_lectures'], 0)

        # Verify weekly timetable is empty
        weekly = dash_data['weekly_timetable']
        for day, lecs in weekly.items():
            self.assertEqual(len(lecs), 0, f"Day {day} should have 0 lectures when no timetable published")

    def test_admin_dashboard_stats_zero_timetables(self):
        tt_col = get_collection('timetables')
        tt_col.delete_many({})
        stats = AdminService.get_dashboard_stats()
        self.assertEqual(stats['active_timetables'], 0, "Admin stats should show 0 active timetables when none created")

if __name__ == '__main__':
    unittest.main()
