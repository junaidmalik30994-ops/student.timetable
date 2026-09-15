import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import get_collection
from app.utils.time_utils import get_ist_now_iso

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class AuthService:

    @staticmethod
    def register_student(full_name, email, roll_number, password, confirm_password,
                         course='B.Tech CS', department='Computer Science & Technology',
                         year='3rd Year', section='Section A', role='student'):
        errors = {}

        # Sanitize inputs
        full_name = full_name.strip() if full_name else ''
        email = email.strip().lower() if email else ''
        roll_number = roll_number.strip().upper() if roll_number else ''
        course = course.strip() if course else ''
        department = department.strip() if department else ''
        year = year.strip() if year else ''
        section = section.strip() if section else ''
        password = password or ''
        confirm_password = confirm_password or ''

        # Validations
        if not full_name:
            errors['full_name'] = 'Full Name is required.'
        elif len(full_name) < 2:
            errors['full_name'] = 'Full Name must be at least 2 characters long.'

        if not email:
            errors['email'] = 'Email Address is required.'
        elif not EMAIL_REGEX.match(email):
            errors['email'] = 'Please enter a valid email address.'

        if not roll_number:
            errors['roll_number'] = 'Roll Number is required.'
        elif len(roll_number) < 3:
            errors['roll_number'] = 'Roll Number must be at least 3 characters.'

        if not course:
            errors['course'] = 'Course selection is required.'

        if not department:
            errors['department'] = 'Department is required.'

        if not year:
            errors['year'] = 'Year selection is required.'

        if not section:
            errors['section'] = 'Section selection is required.'

        # Validate Year/Section combinations for Personal Schedule Only mode
        is_year_other = (year == 'Other')
        is_sec_other = (section == 'Other')

        if is_year_other and is_sec_other:
            schedule_type = 'personal_only'
        elif is_year_other or is_sec_other:
            errors['section'] = 'For Personal Schedule mode, please select Other for both Year and Section.'
        else:
            schedule_type = 'college_and_personal'

        if not password:
            errors['password'] = 'Password is required.'
        elif len(password) < 6:
            errors['password'] = 'Password must be at least 6 characters long.'

        if not confirm_password:
            errors['confirm_password'] = 'Please confirm your password.'
        elif password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match.'

        if errors:
            return False, errors, None

        students = get_collection('students')

        # Check existing email
        existing_email = students.find_one({'email': email})
        if existing_email:
            return False, {'email': 'This email address is already registered.'}, None

        # Check existing roll number
        existing_roll = students.find_one({'roll_number': roll_number})
        if existing_roll:
            return False, {'roll_number': 'This Roll Number is already registered.'}, None

        # Hash password securely
        hashed_password = generate_password_hash(password)

        student_doc = {
            'full_name': full_name,
            'email': email,
            'roll_number': roll_number,
            'password_hash': hashed_password,
            'role': role,
            'course': course,
            'department': department,
            'year': year,
            'section': section,
            'schedule_type': schedule_type,
            'university': 'Shobhit University Gangoh (SUG)',
            'created_at': get_ist_now_iso()
        }

        result = students.insert_one(student_doc)
        student_doc['id'] = str(result.inserted_id)
        
        return True, None, student_doc

    @staticmethod
    def authenticate_student(email, password):
        errors = {}
        email = email.strip().lower() if email else ''
        password = password or ''

        if not email:
            errors['email'] = 'Email address is required.'
        if not password:
            errors['password'] = 'Password is required.'

        if errors:
            return False, errors, None

        students = get_collection('students')
        student = students.find_one({'email': email})

        if not student or not check_password_hash(student.get('password_hash', ''), password):
            return False, {'general': 'Invalid Email Address or Password. Please try again.'}, None

        st_year = student.get('year', '3rd Year')
        st_section = student.get('section', 'Section A')
        default_schedule_type = 'personal_only' if (st_year == 'Other' and st_section == 'Other') else 'college_and_personal'
        schedule_type = student.get('schedule_type', default_schedule_type)

        return True, None, {
            'id': str(student.get('_id', '')),
            'full_name': student.get('full_name'),
            'email': student.get('email'),
            'roll_number': student.get('roll_number'),
            'role': student.get('role', 'student'),
            'course': student.get('course', 'B.Tech CS'),
            'department': student.get('department', 'Computer Science & Technology'),
            'year': st_year,
            'section': st_section,
            'schedule_type': schedule_type
        }

