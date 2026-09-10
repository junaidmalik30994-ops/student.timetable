import re
from datetime import datetime, time, timedelta
from app.utils.db import get_collection, serialize_mongo

class TimetableService:

    @staticmethod
    def parse_time_mins(t_str):
        """Convert any time string (e.g., '09:00', '11:00 AM', '1:00 PM', '13:00') to total minutes from midnight (0-1439)."""
        if not t_str:
            return 0
        try:
            t_str = str(t_str).strip()
            is_pm = 'PM' in t_str.upper()
            is_am = 'AM' in t_str.upper()

            cleaned = re.sub(r'[^0-9:]', '', t_str)
            parts = cleaned.split(':')
            if not parts or not parts[0]:
                return 0

            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 and parts[1] else 0

            if is_pm:
                if hours < 12:
                    hours += 12
            elif is_am:
                if hours == 12:
                    hours = 0

            return hours * 60 + minutes
        except Exception:
            return 0

    @staticmethod
    def format_time_12h(t_str):
        """Format any time string into clean 12-hour AM/PM string representation."""
        mins = TimetableService.parse_time_mins(t_str)
        hours = (mins // 60) % 24
        minutes = mins % 60
        period = 'AM' if hours < 12 else 'PM'
        h12 = hours % 12
        if h12 == 0:
            h12 = 12
        return f"{h12:02d}:{minutes:02d} {period}"


    @staticmethod
    def validate_timetable_entry(entry, day_entries=None, edit_entry_id=None):
        """Validate timetable entry fields, lab duration, and time slot overlaps."""
        errors = {}
        subject = entry.get('subject', '').strip()
        teacher = entry.get('teacher', '').strip()
        start_time = entry.get('start', '').strip()
        end_time = entry.get('end', '').strip()
        entry_type = entry.get('type', 'Lecture').strip()

        if not subject:
            errors['subject'] = 'Subject name is required.'

        if entry_type in ['Lecture', 'Lab'] and not teacher:
            errors['teacher'] = 'Teacher name is required for Lecture and Lab.'

        if not start_time:
            errors['start'] = 'Start time is required.'
        if not end_time:
            errors['end'] = 'End time is required.'

        s_min = TimetableService.parse_time_mins(start_time)
        e_min = TimetableService.parse_time_mins(end_time)

        if start_time and end_time:
            if e_min <= s_min:
                errors['end'] = 'End time must be after Start time.'
            elif entry_type == 'Lab':
                duration = e_min - s_min
                if duration != 120:
                    errors['type'] = 'Lab type entries must have a 2-hour duration (120 minutes).'

        if not errors and day_entries:
            for existing in day_entries:
                ex_id = str(existing.get('id', ''))
                if edit_entry_id and ex_id == str(edit_entry_id):
                    continue
                ex_s = TimetableService.parse_time_mins(existing.get('start', ''))
                ex_e = TimetableService.parse_time_mins(existing.get('end', ''))
                
                # Check overlap
                if (s_min < ex_e) and (e_min > ex_s):
                    errors['general'] = f"Time slot ({start_time}-{end_time}) overlaps with existing entry '{existing.get('subject')}' ({existing.get('start')}-{existing.get('end')})."
                    break

        return len(errors) == 0, errors

    @staticmethod
    def get_class_timetable(course, department, year, section):
        """Retrieve draft or published timetable document for a given class."""
        timetables_col = get_collection('timetables')
        query = {
            'course': course,
            'department': department,
            'year': year,
            'section': section
        }
        # Prefer published active timetable, else fallback to latest draft
        tt = timetables_col.find_one({**query, 'status': 'published'})
        if not tt:
            tt = timetables_col.find_one({**query, 'status': 'draft'})
        if not tt:
            tt = timetables_col.find_one(query)

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        empty_schedule = {day: [] for day in days}

        if not tt:
            return {
                'course': course,
                'department': department,
                'year': year,
                'section': section,
                'status': 'draft',
                'weekly_schedule': empty_schedule
            }

        schedule = tt.get('weekly_schedule') or {}
        res_doc = {
            'id': str(tt.get('_id', '')),
            'course': course,
            'department': department,
            'year': year,
            'section': section,
            'status': tt.get('status', 'draft'),
            'weekly_schedule': {day: schedule.get(day, []) for day in days}
        }
        if '_id' in tt:
            res_doc['_id'] = str(tt['_id'])
        return serialize_mongo(res_doc)

    @staticmethod
    def save_draft_timetable(course, department, year, section, weekly_schedule):
        """Save/update draft timetable for a class."""
        timetables_col = get_collection('timetables')
        query = {
            'course': course,
            'department': department,
            'year': year,
            'section': section
        }
        # Look for existing published/draft document (not archived)
        existing = timetables_col.find_one({**query, 'status': {'$in': ['published', 'draft']}})
        if not existing:
            existing = timetables_col.find_one(query)

        doc = {
            'course': course,
            'department': department,
            'year': year,
            'section': section,
            'status': existing.get('status', 'draft') if existing else 'draft',
            'weekly_schedule': weekly_schedule,
            'updated_at': datetime.utcnow().isoformat()
        }
        if existing:
            timetables_col.update_one({'_id': existing['_id']}, {'$set': doc})
            doc['id'] = str(existing['_id'])
            doc['_id'] = str(existing['_id'])
        else:
            res = timetables_col.insert_one(doc)
            doc['id'] = str(res.inserted_id)
            doc['_id'] = str(res.inserted_id)
        return serialize_mongo(doc)

    @staticmethod
    def publish_timetable(course, department, year, section, weekly_schedule=None):
        """Publish timetable for a class, making it active for students."""
        timetables_col = get_collection('timetables')
        query = {
            'course': course,
            'department': department,
            'year': year,
            'section': section
        }

        # Fetch current draft/doc if weekly_schedule not provided
        if weekly_schedule is None:
            existing = timetables_col.find_one(query)
            weekly_schedule = existing.get('weekly_schedule', {}) if existing else {}

        # Archive old active/draft timetables for this class
        try:
            timetables_col.update_many(query, {'$set': {'status': 'archived', 'is_active': False}})
        except Exception:
            pass

        doc = {
            'course': course,
            'department': department,
            'year': year,
            'section': section,
            'status': 'published',
            'is_active': True,
            'weekly_schedule': weekly_schedule,
            'published_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        res = timetables_col.insert_one(doc)
        doc['id'] = str(res.inserted_id)
        doc['_id'] = str(res.inserted_id)
        return serialize_mongo(doc)

    @staticmethod
    def get_weekly_timetable(student_id=None):
        """Fetch active published timetable matching student's class, or return empty structure."""
        student_course = 'B.Tech CS'
        student_dept = 'Computer Science & Technology'
        student_year = '3rd Year'
        student_sec = 'Section A'

        if student_id:
            students_col = get_collection('students')
            from bson import ObjectId
            st = None
            try:
                st = students_col.find_one({'_id': ObjectId(student_id)})
            except Exception:
                pass
            if not st:
                st = students_col.find_one({'_id': student_id})
            
            if st:
                student_course = st.get('course', student_course)
                student_dept = st.get('department', student_dept)
                student_year = st.get('year', student_year)
                student_sec = st.get('section', student_sec)

        timetables_col = get_collection('timetables')
        active_tt = timetables_col.find_one({
            'course': student_course,
            'department': student_dept,
            'year': student_year,
            'section': student_sec,
            'status': 'published'
        })

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        empty_schedule = {day: [] for day in days}

        if not active_tt:
            return empty_schedule

        schedule = active_tt.get('weekly_schedule') or {}
        return {day: schedule.get(day, []) for day in days}

    @staticmethod
    def get_today_timetable(student_id=None, day_name=None):
        """Fetch student's college timetable for a specific day (or today)."""
        if not day_name:
            day_name = datetime.now().strftime('%A')

        weekly_tt = TimetableService.get_weekly_timetable(student_id)
        day_entries = weekly_tt.get(day_name, [])

        current_time_obj = datetime.now().time()
        current_minutes = current_time_obj.hour * 60 + current_time_obj.minute

        formatted = []
        for lec in day_entries:
            s_min = TimetableService.parse_time_mins(lec.get('start', '00:00'))
            e_min = TimetableService.parse_time_mins(lec.get('end', '00:00'))

            if current_minutes >= e_min:
                status = 'Completed'
            elif current_minutes >= s_min and current_minutes < e_min:
                status = 'Current'
            else:
                status = 'Upcoming'

            formatted.append({
                'id': lec.get('id', 'lec'),
                'subject': lec.get('subject', lec.get('title', 'N/A')),
                'teacher': lec.get('teacher', lec.get('instructor', '-')),
                'start': lec.get('start', ''),
                'end': lec.get('end', ''),
                'type': lec.get('type', 'Lecture'),
                'status': status
            })
        return formatted

    @staticmethod
    def get_student_tasks(student_id):
        """Fetch all personal tasks for student from MongoDB."""
        tasks_col = get_collection('tasks')
        db_tasks = list(tasks_col.find({'student_id': student_id}))
        
        today_str = datetime.now().strftime('%Y-%m-%d')
        formatted = []
        for t in db_tasks:
            raw_start = t.get('start', '05:00 PM')
            raw_end = t.get('end', '06:00 PM')
            formatted.append({
                'id': str(t.get('_id', t.get('id'))),
                'title': t.get('title', ''),
                'date': t.get('date', today_str),
                'start': TimetableService.format_time_12h(raw_start) if raw_start else '05:00 PM',
                'end': TimetableService.format_time_12h(raw_end) if raw_end else '06:00 PM',
                'completed': t.get('completed', False)
            })
        
        # Sort by date & start time
        formatted.sort(key=lambda x: (x['date'], TimetableService.parse_time_mins(x['start'])))
        return formatted

    @staticmethod
    def add_personal_task(student_id, title, date_str=None, start_time='17:00', end_time='18:00'):
        tasks_col = get_collection('tasks')
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        doc = {
            'student_id': student_id,
            'title': title,
            'date': date_str,
            'start': start_time,
            'end': end_time,
            'completed': False,
            'created_at': datetime.utcnow().isoformat()
        }
        res = tasks_col.insert_one(doc)
        doc['id'] = str(res.inserted_id)
        doc['_id'] = str(res.inserted_id)
        return serialize_mongo(doc)

    @staticmethod
    def update_personal_task(student_id, task_id, title, date_str, start_time, end_time):
        tasks_col = get_collection('tasks')
        from bson import ObjectId
        target = None
        try:
            target = tasks_col.find_one({'_id': ObjectId(task_id), 'student_id': student_id})
        except Exception:
            pass
        if not target:
            target = tasks_col.find_one({'_id': task_id, 'student_id': student_id})

        if target:
            update_data = {
                'title': title,
                'date': date_str,
                'start': start_time,
                'end': end_time,
                'updated_at': datetime.utcnow().isoformat()
            }
            tasks_col.update_one({'_id': target['_id']}, {'$set': update_data})
            update_data['id'] = str(target['_id'])
            update_data['_id'] = str(target['_id'])
            update_data['completed'] = target.get('completed', False)
            return True, serialize_mongo(update_data)
        return False, None

    @staticmethod
    def toggle_personal_task(student_id, task_id):
        tasks_col = get_collection('tasks')
        from bson import ObjectId
        target = None
        try:
            target = tasks_col.find_one({'_id': ObjectId(task_id), 'student_id': student_id})
        except Exception:
            pass
        if not target:
            target = tasks_col.find_one({'_id': task_id, 'student_id': student_id})
        
        if target:
            new_val = not target.get('completed', False)
            target_id = target.get('_id')
            tasks_col.update_one({'_id': target_id}, {'$set': {'completed': new_val}})
            target['completed'] = new_val
            target['id'] = str(target.get('_id'))
            target['_id'] = str(target.get('_id'))
            return True, serialize_mongo(target)
        return False, None

    @staticmethod
    def delete_personal_task(student_id, task_id):
        tasks_col = get_collection('tasks')
        from bson import ObjectId
        target = None
        try:
            target = tasks_col.find_one({'_id': ObjectId(task_id), 'student_id': student_id})
        except Exception:
            pass
        if not target:
            target = tasks_col.find_one({'_id': task_id, 'student_id': student_id})
        
        if target:
            target_id = target.get('_id')
            tasks_col.delete_one({'_id': target_id})
            return True
        return False

    @staticmethod
    def get_today_dashboard_data(student_id, target_datetime=None):
        if target_datetime is None:
            now = datetime.now()
        else:
            now = target_datetime

        day_name = now.strftime('%A')
        today_date_str = now.strftime('%Y-%m-%d')
        current_time_obj = now.time()
        current_minutes = current_time_obj.hour * 60 + current_time_obj.minute

        weekly_timetable = TimetableService.get_weekly_timetable(student_id)
        today_lectures = weekly_timetable.get(day_name, [])
        all_student_tasks = TimetableService.get_student_tasks(student_id)

        # Filter personal tasks scheduled for today's date
        today_tasks = [t for t in all_student_tasks if t.get('date') == today_date_str]

        # Merge college timetable entries & today's personal tasks into today's schedule timeline
        timeline = []

        # Process college lectures & labs
        total_lectures = len(today_lectures)
        completed_lectures = 0
        remaining_lectures = 0

        for lec in today_lectures:
            s_min = TimetableService.parse_time_mins(lec.get('start', '00:00'))
            e_min = TimetableService.parse_time_mins(lec.get('end', '00:00'))

            if current_minutes >= e_min:
                status = 'Completed'
                completed_lectures += 1
            elif current_minutes >= s_min and current_minutes < e_min:
                status = 'Current'
            else:
                status = 'Upcoming'
                remaining_lectures += 1

            sub_title = lec.get('subject', lec.get('title', 'Subject'))
            teacher = lec.get('teacher', lec.get('instructor', ''))
            lec_type = lec.get('type', 'Lecture')
            subtitle_str = f"Teacher: {teacher}" if teacher else f"Type: {lec_type}"

            timeline.append({
                'id': lec.get('id', 'lec'),
                'item_type': 'lecture',
                'title': sub_title,
                'subtitle': subtitle_str,
                'teacher': teacher,
                'type_badge': lec_type,
                'start': lec.get('start', ''),
                'end': lec.get('end', ''),
                'start_min': s_min,
                'end_min': e_min,
                'status': status,
                'raw': lec
            })

        # Process today's personal tasks
        total_tasks = len(all_student_tasks)
        pending_tasks = sum(1 for t in all_student_tasks if not t.get('completed', False))

        for t in today_tasks:
            s_min = TimetableService.parse_time_mins(t.get('start', '00:00'))
            e_min = TimetableService.parse_time_mins(t.get('end', '00:00'))
            is_completed = t.get('completed', False)

            if is_completed or current_minutes >= e_min:
                status = 'Completed'
            elif current_minutes >= s_min and current_minutes < e_min:
                status = 'Current'
            else:
                status = 'Upcoming'

            timeline.append({
                'id': t['id'],
                'item_type': 'task',
                'title': t['title'],
                'subtitle': f"Personal Task • {t.get('date', today_date_str)}",
                'type_badge': 'Personal Task',
                'start': t.get('start', ''),
                'end': t.get('end', ''),
                'start_min': s_min,
                'end_min': e_min,
                'status': status,
                'completed': is_completed,
                'raw': t
            })

        # Sort combined timeline chronologically by start time
        timeline.sort(key=lambda x: x['start_min'])

        # Determine CURRENT ACTIVITY and NEXT UP
        current_activity = None
        next_up = None

        current_candidates = [item for item in timeline if item['status'] == 'Current']
        if current_candidates:
            current_item = current_candidates[0]
            rem_min = current_item['end_min'] - current_minutes
            current_activity = {
                'title': current_item['title'],
                'subtitle': current_item['subtitle'],
                'item_type': current_item['item_type'],
                'badge': current_item['type_badge'],
                'start': current_item['start'],
                'end': current_item['end'],
                'remaining_mins': rem_min,
                'remaining_str': f"{rem_min} mins remaining",
                'status': 'LIVE NOW' if current_item['item_type'] == 'lecture' else 'In Progress'
            }
        else:
            current_activity = {
                'title': 'No current lecture',
                'subtitle': 'No timetable available' if not today_lectures else 'No class scheduled at this time.',
                'item_type': 'free',
                'badge': 'No Class',
                'start': '-',
                'end': '-',
                'remaining_mins': 0,
                'remaining_str': '0 mins remaining',
                'status': 'Inactive'
            }

        upcoming_candidates = [item for item in timeline if item['start_min'] > current_minutes]
        if upcoming_candidates:
            next_item = upcoming_candidates[0]
            time_until = next_item['start_min'] - current_minutes
            if time_until > 60:
                hours = time_until // 60
                mins = time_until % 60
                until_str = f"Starts in {hours}h {mins}m"
            else:
                until_str = f"Starts in {time_until} mins"

            next_up = {
                'title': next_item['title'],
                'subtitle': next_item['subtitle'],
                'item_type': next_item['item_type'],
                'badge': next_item['type_badge'],
                'start': next_item['start'],
                'end': next_item['end'],
                'time_until_mins': time_until,
                'time_until_str': until_str
            }
        else:
            next_up = {
                'title': 'No upcoming activity',
                'subtitle': 'No future classes or tasks scheduled for today.',
                'item_type': 'free',
                'badge': 'No Class',
                'start': '-',
                'end': '-',
                'time_until_mins': 0,
                'time_until_str': 'No upcoming activities'
            }

        return {
            'day_name': day_name,
            'today_date_str': today_date_str,
            'current_time_str': now.strftime('%I:%M %p'),
            'current_activity': current_activity,
            'next_up': next_up,
            'overview': {
                'total_lectures': total_lectures,
                'completed_lectures': completed_lectures,
                'remaining_lectures': remaining_lectures,
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks
            },
            'timeline': timeline,
            'weekly_timetable': weekly_timetable,
            'personal_tasks': all_student_tasks
        }


