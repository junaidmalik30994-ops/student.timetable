from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from app.services.timetable_service import TimetableService
from app.utils.db import serialize_mongo

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('student_id'):
            flash('Please log in to access the Student Portal.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    student_id = session.get('student_id')
    dash_data = TimetableService.get_today_dashboard_data(student_id)
    
    student_info = {
        'name': session.get('student_name', 'Student'),
        'email': session.get('student_email', ''),
        'roll_number': session.get('roll_number', ''),
        'department': session.get('department', 'Computer Science & Technology'),
        'role': session.get('role', 'student')
    }

    return render_template(
        'dashboard.html',
        student=student_info,
        dash_data=dash_data
    )

@dashboard_bp.route('/api/dashboard-data', methods=['GET'])
@login_required
def get_dashboard_data():
    student_id = session.get('student_id')
    dash_data = TimetableService.get_today_dashboard_data(student_id)
    return jsonify(serialize_mongo(dash_data))

@dashboard_bp.route('/api/timetable/today', methods=['GET'])
@login_required
def get_today_timetable():
    student_id = session.get('student_id')
    day_name = request.args.get('day', '').strip()
    timetable_entries = TimetableService.get_today_timetable(student_id, day_name=day_name if day_name else None)
    return jsonify({'success': True, 'entries': serialize_mongo(timetable_entries), 'day_name': day_name})

@dashboard_bp.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    student_id = session.get('student_id')
    data = request.get_json() or {}

    title = data.get('title', '').strip()
    date_str = data.get('date', '').strip()
    start_time = data.get('start', '05:00 PM').strip()
    end_time = data.get('end', '06:00 PM').strip()

    if not title:
        return jsonify({'success': False, 'message': 'Task title is required.'}), 400

    s_min = TimetableService.parse_time_mins(start_time)
    e_min = TimetableService.parse_time_mins(end_time)
    if e_min <= s_min:
        return jsonify({'success': False, 'message': 'End time must be after Start time.'}), 400

    formatted_start = TimetableService.format_time_12h(start_time)
    formatted_end = TimetableService.format_time_12h(end_time)

    new_task = TimetableService.add_personal_task(
        student_id=student_id,
        title=title,
        date_str=date_str,
        start_time=formatted_start,
        end_time=formatted_end
    )

    return jsonify({'success': True, 'task': serialize_mongo(new_task), 'message': 'Personal task created successfully.'})

@dashboard_bp.route('/api/tasks/<task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    student_id = session.get('student_id')
    data = request.get_json() or {}

    title = data.get('title', '').strip()
    date_str = data.get('date', '').strip()
    start_time = data.get('start', '05:00 PM').strip()
    end_time = data.get('end', '06:00 PM').strip()

    if not title:
        return jsonify({'success': False, 'message': 'Task title is required.'}), 400

    s_min = TimetableService.parse_time_mins(start_time)
    e_min = TimetableService.parse_time_mins(end_time)
    if e_min <= s_min:
        return jsonify({'success': False, 'message': 'End time must be after Start time.'}), 400

    formatted_start = TimetableService.format_time_12h(start_time)
    formatted_end = TimetableService.format_time_12h(end_time)

    success, updated_task = TimetableService.update_personal_task(
        student_id=student_id,
        task_id=task_id,
        title=title,
        date_str=date_str,
        start_time=formatted_start,
        end_time=formatted_end
    )

    if success:
        return jsonify({'success': True, 'task': serialize_mongo(updated_task), 'message': 'Personal task updated successfully.'})
    return jsonify({'success': False, 'message': 'Task not found.'}), 404

@dashboard_bp.route('/api/tasks/<task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    student_id = session.get('student_id')
    success, task = TimetableService.toggle_personal_task(student_id, task_id)
    if success:
        return jsonify({'success': True, 'task': serialize_mongo(task), 'message': 'Task status updated.'})
    return jsonify({'success': False, 'message': 'Task not found.'}), 404

@dashboard_bp.route('/api/tasks/<task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    student_id = session.get('student_id')
    success = TimetableService.delete_personal_task(student_id, task_id)
    if success:
        return jsonify({'success': True, 'message': 'Task deleted successfully.'})
    return jsonify({'success': False, 'message': 'Task not found.'}), 404
