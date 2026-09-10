import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import get_collection

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class AdminService:

    @staticmethod
    def ensure_default_admin():
        """Ensure at least one default administrator exists in the database."""
        admins = get_collection('admins')
        existing = admins.find_one({'email': 'admin@shobhituniversity.ac.in'})
        if not existing:
            default_admin = {
                'full_name': 'System Administrator',
                'email': 'admin@shobhituniversity.ac.in',
                'password_hash': generate_password_hash('admin123'),
                'role': 'admin',
                'department': 'Computer Science & Technology',
                'university': 'Shobhit University Gangoh (SUG)',
                'created_at': datetime.utcnow().isoformat()
            }
            admins.insert_one(default_admin)

    @staticmethod
    def authenticate_admin(email, password):
        """Authenticate administrator credentials."""
        errors = {}
        email = email.strip().lower() if email else ''
        password = password or ''

        if not email:
            errors['email'] = 'Email address is required.'
        if not password:
            errors['password'] = 'Password is required.'

        if errors:
            return False, errors, None

        admins = get_collection('admins')
        admin = admins.find_one({'email': email})

        if not admin or not check_password_hash(admin.get('password_hash', ''), password):
            return False, {'general': 'Invalid Admin Email Address or Password. Please try again.'}, None

        return True, None, {
            'id': str(admin.get('_id', '')),
            'full_name': admin.get('full_name', 'System Administrator'),
            'email': admin.get('email'),
            'role': admin.get('role', 'admin'),
            'department': admin.get('department', 'Computer Science & Technology')
        }

    @staticmethod
    def get_dashboard_stats():
        """Fetch overview statistics using real MongoDB data."""
        students_col = get_collection('students')
        timetables_col = get_collection('timetables')

        # Count total registered students in MongoDB
        try:
            total_students = len(list(students_col.find({})))
        except Exception:
            total_students = 0

        # Count active timetables in MongoDB
        try:
            active_timetables = len(list(timetables_col.find({})))
        except Exception:
            active_timetables = 0

        return {
            'total_students': total_students,
            'active_timetables': active_timetables
        }

    @staticmethod
    def get_all_students(search_query=None):
        """Fetch real registered students list with search capability."""
        students_col = get_collection('students')
        all_docs = list(students_col.find({}))
        
        students_list = []
        for doc in all_docs:
            created_at_str = doc.get('created_at', '')
            formatted_date = created_at_str
            if created_at_str:
                try:
                    dt = datetime.fromisoformat(created_at_str.replace('Z', ''))
                    formatted_date = dt.strftime('%b %d, %Y - %I:%M %p')
                except Exception:
                    formatted_date = created_at_str[:10]

            student_obj = {
                'id': str(doc.get('_id', '')),
                'full_name': doc.get('full_name', 'N/A'),
                'email': doc.get('email', 'N/A'),
                'roll_number': doc.get('roll_number', 'N/A'),
                'course': doc.get('course', 'B.Tech CS'),
                'department': doc.get('department', 'Computer Science & Technology'),
                'year': doc.get('year', '3rd Year'),
                'section': doc.get('section', 'Section A'),
                'created_at': formatted_date
            }
            students_list.append(student_obj)

        if search_query:
            query_lower = search_query.strip().lower()
            students_list = [
                s for s in students_list
                if query_lower in s['full_name'].lower()
                or query_lower in s['email'].lower()
                or query_lower in s['roll_number'].lower()
                or query_lower in s['course'].lower()
                or query_lower in s['year'].lower()
                or query_lower in s['section'].lower()
            ]

        # Sort newest students first
        students_list.reverse()
        return students_list

    @staticmethod
    def update_admin_password(admin_id, current_password, new_password, confirm_password):
        """Update admin password securely."""
        errors = {}

        if not current_password:
            errors['current_password'] = 'Current password is required.'
        if not new_password:
            errors['new_password'] = 'New password is required.'
        elif len(new_password) < 6:
            errors['new_password'] = 'New password must be at least 6 characters.'
        if not confirm_password:
            errors['confirm_password'] = 'Please confirm new password.'
        elif new_password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'

        if errors:
            return False, errors

        admins = get_collection('admins')
        admin = None
        from bson import ObjectId
        try:
            admin = admins.find_one({'_id': ObjectId(admin_id)})
        except Exception:
            pass
        if not admin:
            admin = admins.find_one({'_id': admin_id})

        if not admin:
            admin = admins.find_one({'role': 'admin'})

        if not admin or not check_password_hash(admin.get('password_hash', ''), current_password):
            return False, {'current_password': 'Incorrect current password.'}

        new_hash = generate_password_hash(new_password)
        admins.update_one({'_id': admin['_id']}, {'$set': {'password_hash': new_hash}})
        return True, None
