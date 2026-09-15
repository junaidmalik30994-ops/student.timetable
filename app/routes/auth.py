from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('student_id'):
        return redirect(url_for('dashboard.index'))

    errors = {}
    form_data = {
        'full_name': '',
        'email': '',
        'roll_number': '',
        'course': 'B.Tech CS',
        'department': 'Computer Science & Technology',
        'year': '3rd Year',
        'section': 'Section A',
        'password': '',
        'confirm_password': ''
    }

    if request.method == 'POST':
        form_data['full_name'] = request.form.get('full_name', '').strip()
        form_data['email'] = request.form.get('email', '').strip()
        form_data['roll_number'] = request.form.get('roll_number', '').strip()
        form_data['course'] = request.form.get('course', 'B.Tech CS').strip()
        form_data['department'] = request.form.get('department', 'Computer Science & Technology').strip()
        form_data['year'] = request.form.get('year', '3rd Year').strip()
        form_data['section'] = request.form.get('section', 'Section A').strip()
        form_data['password'] = request.form.get('password', '')
        form_data['confirm_password'] = request.form.get('confirm_password', '')

        success, validation_errors, student = AuthService.register_student(
            full_name=form_data['full_name'],
            email=form_data['email'],
            roll_number=form_data['roll_number'],
            password=form_data['password'],
            confirm_password=form_data['confirm_password'],
            course=form_data['course'],
            department=form_data['department'],
            year=form_data['year'],
            section=form_data['section']
        )

        if success:
            flash('Registration successful! Please log in with your credentials.', 'success')
            return redirect(url_for('auth.login'))
        else:
            errors = validation_errors

    return render_template('register.html', errors=errors, form_data=form_data)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('student_id'):
        return redirect(url_for('dashboard.index'))

    errors = {}
    form_data = {
        'email': '',
        'password': ''
    }

    if request.method == 'POST':
        form_data['email'] = request.form.get('email', '').strip()
        form_data['password'] = request.form.get('password', '')

        success, validation_errors, student = AuthService.authenticate_student(
            email=form_data['email'],
            password=form_data['password']
        )

        if success:
            session['student_id'] = student['id']
            session['student_name'] = student['full_name']
            session['student_email'] = student['email']
            session['roll_number'] = student['roll_number']
            session['course'] = student['course']
            session['department'] = student['department']
            session['year'] = student['year']
            session['section'] = student['section']
            session['role'] = student['role']
            session['schedule_type'] = student.get('schedule_type', 'college_and_personal')
            flash(f'Welcome back, {student["full_name"]}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            errors = validation_errors

    return render_template('login.html', errors=errors, form_data=form_data)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
