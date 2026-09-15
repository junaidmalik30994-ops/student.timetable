import unittest
from datetime import datetime, timezone, timedelta
from app import create_app
from app.services.auth_service import AuthService
from app.services.admin_service import AdminService
from app.utils.db import get_collection
from app.utils.time_utils import IST, format_registration_time

class TestRegistrationIST(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_student_registration_ist_timestamp(self):
        roll_no = "SUG2026IST999"
        email = "ist_student_test@shobhituniversity.ac.in"

        # Register a new student
        success, errors, student_doc = AuthService.register_student(
            full_name="IST Test Student",
            email=email,
            roll_number=roll_no,
            password="password123",
            confirm_password="password123"
        )
        self.assertTrue(success, f"Registration failed with errors: {errors}")
        self.assertIsNotNone(student_doc)

        raw_created_at = student_doc.get('created_at')
        print(f"\n[DEBUG] Raw created_at stored in DB: {raw_created_at}")

        # Check raw stored timestamp contains IST timezone offset (+05:30)
        self.assertIn('+05:30', raw_created_at)

        # Retrieve student list via AdminService
        students_list = AdminService.get_all_students()
        registered_student = next((s for s in students_list if s['roll_number'] == roll_no), None)
        self.assertIsNotNone(registered_student, "Registered student not found in Admin list")

        formatted_created_at = registered_student.get('created_at')
        print(f"[DEBUG] Formatted created_at displayed in Admin Student List: {formatted_created_at}")

        # Verify formatting matches DD Month YYYY, hh:mm AM/PM (e.g. 12 September 2026, 08:53 AM)
        now_ist = datetime.now(IST)
        expected_date_part = now_ist.strftime('%d %B %Y')
        self.assertIn(expected_date_part, formatted_created_at)

    def test_legacy_utc_timestamp_conversion_to_ist(self):
        # Insert a legacy student with UTC naive ISO timestamp (e.g. 09:00:00 UTC -> 14:30:00 IST / 02:30 PM IST)
        students_col = get_collection('students')
        legacy_roll = "SUGLEGACY001"
        students_col.delete_many({'roll_number': legacy_roll})

        students_col.insert_one({
            'full_name': 'Legacy Student',
            'email': 'legacy@shobhituniversity.ac.in',
            'roll_number': legacy_roll,
            'created_at': '2026-09-11T09:00:00'
        })

        students_list = AdminService.get_all_students()
        legacy_student = next((s for s in students_list if s['roll_number'] == legacy_roll), None)
        self.assertIsNotNone(legacy_student)

        # 09:00 UTC should be formatted as 11 September 2026, 02:30 PM
        self.assertEqual(legacy_student['created_at'], '11 September 2026, 02:30 PM')
        print(f"[DEBUG] Legacy UTC timestamp correctly converted to IST: {legacy_student['created_at']}")

if __name__ == '__main__':
    unittest.main()
