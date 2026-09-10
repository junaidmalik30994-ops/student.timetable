import logging
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.services.admin_service import AdminService
from app.utils.db import serialize_mongo

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id') or session.get('admin_role') != 'admin':
            flash('Unauthorized Access: Please log in with Administrator credentials.', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_id') and session.get('admin_role') == 'admin':
        return redirect(url_for('admin.dashboard'))

    errors = {}
    form_data = {
        'email': '',
        'password': ''
    }

    if request.method == 'POST':
        form_data['email'] = request.form.get('email', '').strip()
        form_data['password'] = request.form.get('password', '')

        success, validation_errors, admin = AdminService.authenticate_admin(
            email=form_data['email'],
            password=form_data['password']
        )

        if success:
            # Clear student session to keep sessions completely separate
            session.pop('student_id', None)
            session.pop('student_name', None)
            session.pop('student_email', None)
            session.pop('roll_number', None)
            
            # Set separate admin session variables
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['full_name']
            session['admin_email'] = admin['email']
            session['admin_role'] = admin['role']
            session['department'] = admin['department']
            
            flash(f'Welcome, Admin {admin["full_name"]}!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            errors = validation_errors

    # Crucial requirement: Email & Password MUST be blank on initial page load (GET)
    return render_template('admin/admin_login.html', errors=errors, form_data=form_data)

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = AdminService.get_dashboard_stats()
    admin_info = {
        'name': session.get('admin_name', 'System Administrator'),
        'email': session.get('admin_email', 'admin@shobhituniversity.ac.in'),
        'role': 'Administrator',
        'department': session.get('department', 'Computer Science & Technology')
    }
    return render_template('admin/admin_dashboard.html', admin=admin_info, stats=stats, active_nav='dashboard')

@admin_bp.route('/timetable')
@admin_required
def timetable():
    admin_info = {
        'name': session.get('admin_name', 'System Administrator'),
        'email': session.get('admin_email', 'admin@shobhituniversity.ac.in'),
        'role': 'Administrator',
        'department': session.get('department', 'Computer Science & Technology')
    }
    return render_template('admin/admin_timetable.html', admin=admin_info, active_nav='timetable')

@admin_bp.route('/api/timetable/load', methods=['GET'])
@admin_required
def load_class_timetable():
    try:
        course = request.args.get('course', 'B.Tech CS').strip()
        department = request.args.get('department', 'Computer Science & Technology').strip()
        year = request.args.get('year', '3rd Year').strip()
        section = request.args.get('section', 'Section A').strip()

        from app.services.timetable_service import TimetableService
        data = TimetableService.get_class_timetable(course, department, year, section)
        return jsonify({'success': True, 'timetable': serialize_mongo(data)})
    except Exception as e:
        logger.error(f"Error loading timetable: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Failed to load timetable: {str(e)}'}), 500

@admin_bp.route('/api/timetable/validate', methods=['POST'])
@admin_required
def validate_entry():
    try:
        data = request.get_json() or {}
        entry = data.get('entry', {})
        day_entries = data.get('day_entries', [])
        edit_id = data.get('edit_entry_id')

        from app.services.timetable_service import TimetableService
        valid, errors = TimetableService.validate_timetable_entry(entry, day_entries, edit_id)
        return jsonify({'success': valid, 'errors': serialize_mongo(errors)})
    except Exception as e:
        logger.error(f"Error validating timetable entry: {e}", exc_info=True)
        return jsonify({'success': False, 'errors': {'general': str(e)}}), 500

@admin_bp.route('/api/timetable/save', methods=['POST'])
@admin_required
def save_draft():
    try:
        data = request.get_json() or {}
        course = data.get('course', 'B.Tech CS').strip()
        department = data.get('department', 'Computer Science & Technology').strip()
        year = data.get('year', '3rd Year').strip()
        section = data.get('section', 'Section A').strip()
        weekly_schedule = data.get('weekly_schedule', {})

        from app.services.timetable_service import TimetableService
        saved = TimetableService.save_draft_timetable(course, department, year, section, weekly_schedule)
        return jsonify({'success': True, 'timetable': serialize_mongo(saved), 'message': 'Draft timetable saved successfully.'})
    except Exception as e:
        logger.error(f"Error saving draft timetable: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Failed to save draft: {str(e)}'}), 500

@admin_bp.route('/api/timetable/publish', methods=['POST'])
@admin_required
def publish_timetable():
    try:
        data = request.get_json() or {}
        course = data.get('course', 'B.Tech CS').strip()
        department = data.get('department', 'Computer Science & Technology').strip()
        year = data.get('year', '3rd Year').strip()
        section = data.get('section', 'Section A').strip()
        weekly_schedule = data.get('weekly_schedule', {})

        from app.services.timetable_service import TimetableService
        pub = TimetableService.publish_timetable(course, department, year, section, weekly_schedule)
        return jsonify({'success': True, 'timetable': serialize_mongo(pub), 'message': f'Timetable for {course} ({year} {section}) published successfully!'})
    except Exception as e:
        logger.error(f"Error publishing timetable: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Failed to publish timetable: {str(e)}'}), 500


@admin_bp.route('/students')
@admin_required
def students():
    search_query = request.args.get('q', '').strip()
    student_list = AdminService.get_all_students(search_query=search_query)
    admin_info = {
        'name': session.get('admin_name', 'System Administrator'),
        'email': session.get('admin_email', 'admin@shobhituniversity.ac.in'),
        'role': 'Administrator',
        'department': session.get('department', 'Computer Science & Technology')
    }
    return render_template(
        'admin/admin_students.html',
        admin=admin_info,
        students=student_list,
        search_query=search_query,
        active_nav='students'
    )

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    admin_info = {
        'name': session.get('admin_name', 'System Administrator'),
        'email': session.get('admin_email', 'admin@shobhituniversity.ac.in'),
        'role': 'Administrator',
        'department': session.get('department', 'Computer Science & Technology')
    }
    
    errors = {}
    success_msg = None

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'change_password':
            current_pass = request.form.get('current_password', '')
            new_pass = request.form.get('new_password', '')
            confirm_pass = request.form.get('confirm_password', '')

            ok, val_errs = AdminService.update_admin_password(
                admin_id=session.get('admin_id'),
                current_password=current_pass,
                new_password=new_pass,
                confirm_password=confirm_pass
            )
            if ok:
                flash('Password updated successfully.', 'success')
                return redirect(url_for('admin.settings'))
            else:
                errors = val_errs

    return render_template(
        'admin/admin_settings.html',
        admin=admin_info,
        errors=errors,
        active_nav='settings'
    )

@admin_bp.route('/logout')
def logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('admin_email', None)
    session.pop('admin_role', None)
    flash('Admin session logged out successfully.', 'info')
    return redirect(url_for('admin.login'))
