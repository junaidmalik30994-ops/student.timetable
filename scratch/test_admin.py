import sys
import unittest
from app import create_app
from app.utils.db import get_collection
from app.services.admin_service import AdminService

class TestAdminPortal(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_default_admin_created(self):
        admins = get_collection('admins')
        admin = admins.find_one({'email': 'admin@shobhituniversity.ac.in'})
        self.assertIsNotNone(admin)
        self.assertEqual(admin['role'], 'admin')

    def test_admin_login_page_renders_blank_inputs(self):
        response = self.client.get('/admin/login')
        self.assertEqual(response.status_code, 200)
        html = response.data.decode('utf-8')
        self.assertIn('Admin Login', html)
        self.assertIn('Back to Student Login', html)
        # Check email and password inputs are blank
        self.assertIn('name="email"', html)
        self.assertIn('value=""', html)

    def test_admin_login_success_and_protection(self):
        # 1. Access protected admin route without login -> should redirect to login
        response = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b'Unauthorized Access', response.data)

        # 2. Login with valid admin credentials
        login_res = self.client.post('/admin/login', data={
            'email': 'admin@shobhituniversity.ac.in',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Welcome, Admin', login_res.data)

        # 3. Access admin dashboard after login
        dash_res = self.client.get('/admin/dashboard')
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn(b'Total Registered Students', dash_res.data)
        self.assertIn(b'Active Timetables', dash_res.data)

        # 4. Access timetable phase 2 page
        tt_res = self.client.get('/admin/timetable')
        self.assertEqual(tt_res.status_code, 200)
        self.assertIn(b'Manual Weekly Timetable Builder', tt_res.data)
        self.assertNotIn(b'Upload Timetable PDF', tt_res.data)

        # 5. Access student list page
        students_res = self.client.get('/admin/students')
        self.assertEqual(students_res.status_code, 200)
        self.assertIn(b'Registered Student List', students_res.data)

        # 6. Access admin settings page
        settings_res = self.client.get('/admin/settings')
        self.assertEqual(settings_res.status_code, 200)
        self.assertIn(b'Admin Settings', settings_res.data)

        # 7. Logout
        logout_res = self.client.get('/admin/logout', follow_redirects=True)
        self.assertIn(b'Admin session logged out successfully', logout_res.data)

if __name__ == '__main__':
    unittest.main()
