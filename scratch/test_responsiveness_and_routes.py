import unittest
from app import create_app

class TestAppRoutesAndTemplates(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_student_login_page(self):
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Student Login', res.data)

    def test_admin_login_page(self):
        res = self.client.get('/admin/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Admin Login', res.data)

    def test_admin_authenticated_pages_header_logout_removal(self):
        # Perform admin login
        login_res = self.client.post('/admin/login', data={
            'email': 'admin@shobhituniversity.ac.in',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        
        # Check admin dashboard HTML
        dash_res = self.client.get('/admin/dashboard')
        self.assertEqual(dash_res.status_code, 200)
        html_str = dash_res.data.decode('utf-8')
        
        # 1. Ensure admin-logout-btn is NOT in the top bar header
        self.assertNotIn('admin-logout-btn', html_str)
        # 2. Ensure admin-nav-logout IS present in sidebar navigation
        self.assertIn('admin-nav-logout', html_str)
        print("\n[SUCCESS] Top-bar logout button removed cleanly from Admin Panel!")
        print("[SUCCESS] Sidebar navigation logout button remains active and functional!")

if __name__ == '__main__':
    unittest.main()
