document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initSidebarNavigation();
    initTabNavigation();
    initSubTabNavigation();
    initLiveClock();
    initTaskForm();
    initTaskActions();
    initTaskEditModal();
    initStudentDayFilter();
    initAdminTimetable();
});

/* ==========================================
   1. THEME SWITCHER (Light / Dark Mode)
   ========================================== */
function initThemeToggle() {
    const themeBtn = document.getElementById('themeToggleBtn');
    const htmlElement = document.documentElement;

    const savedTheme = localStorage.getItem('sug_theme') || 'light';
    htmlElement.setAttribute('data-theme', savedTheme);

    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('sug_theme', newTheme);
        });
    }
}

/* ==========================================
   2. SIDEBAR DRAWER & MOBILE NAVIGATION
   ========================================== */
function initSidebarNavigation() {
    const hamburgerBtn = document.getElementById('hamburgerMenuBtn');
    const headerMobileBtn = document.getElementById('headerMobileMenuBtn');
    const closeBtn = document.getElementById('btnCloseSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const drawer = document.getElementById('sidebarDrawer');
    const adminToggleBtn = document.getElementById('adminMobileNavToggle');
    const adminNavBar = document.querySelector('.admin-nav-bar');

    function openSidebar() {
        if (drawer && overlay) {
            drawer.classList.add('open');
            overlay.classList.add('open');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeSidebar() {
        if (drawer && overlay) {
            drawer.classList.remove('open');
            overlay.classList.remove('open');
            document.body.style.overflow = '';
        }
    }

    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openSidebar();
        });
    }

    if (headerMobileBtn) {
        headerMobileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openSidebar();
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', closeSidebar);
    }

    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    if (adminToggleBtn && adminNavBar) {
        adminToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            adminNavBar.classList.toggle('mobile-open');
        });
    }

    document.addEventListener('click', (e) => {
        if (adminNavBar && adminNavBar.classList.contains('mobile-open')) {
            if (!adminNavBar.contains(e.target) && adminToggleBtn && !adminToggleBtn.contains(e.target)) {
                adminNavBar.classList.remove('mobile-open');
            }
        }
    });

    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (drawer && drawer.classList.contains('open')) {
                closeSidebar();
            }
            if (adminNavBar && adminNavBar.classList.contains('mobile-open')) {
                adminNavBar.classList.remove('mobile-open');
            }
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            closeSidebar();
            if (adminNavBar && adminNavBar.classList.contains('mobile-open')) {
                adminNavBar.classList.remove('mobile-open');
            }
        }
    });

    window.closeSidebarDrawer = closeSidebar;
}

/* ==========================================
   3. MAIN TAB NAVIGATION
   ========================================== */
function initTabNavigation() {
    const navTabs = document.querySelectorAll('.nav-tab');
    const viewPanels = document.querySelectorAll('.view-panel');

    if (!navTabs.length) return;

    const activeTabId = sessionStorage.getItem('sug_active_tab') || 'dashboard-view';
    switchTab(activeTabId);

    navTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            const targetTab = tab.getAttribute('data-tab');
            if (targetTab) {
                switchTab(targetTab);
                sessionStorage.setItem('sug_active_tab', targetTab);
                if (window.closeSidebarDrawer) {
                    window.closeSidebarDrawer();
                }
            }
        });
    });

    function switchTab(tabId) {
        navTabs.forEach(t => {
            if (t.getAttribute('data-tab') === tabId) {
                t.classList.add('active');
            } else {
                t.classList.remove('active');
            }
        });

        viewPanels.forEach(panel => {
            if (panel.id === tabId) {
                panel.classList.add('active');
            } else {
                panel.classList.remove('active');
            }
        });
    }
}

/* ==========================================
   3. SUB-TAB NAVIGATION
   ========================================== */
function initSubTabNavigation() {
    const subTabBtns = document.querySelectorAll('.sub-tab-btn');

    subTabBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const targetSubtab = btn.getAttribute('data-subtab');
            const parentView = btn.closest('.view-panel');

            if (parentView && targetSubtab) {
                const peerBtns = parentView.querySelectorAll('.sub-tab-btn');
                const peerPanels = parentView.querySelectorAll('.subview-panel');

                peerBtns.forEach(b => b.classList.remove('active'));
                peerPanels.forEach(p => p.classList.remove('active'));

                btn.classList.add('active');
                const targetPanel = parentView.querySelector(`#${targetSubtab}`);
                if (targetPanel) {
                    targetPanel.classList.add('active');
                }
            }
        });
    });
}

/* ==========================================
   4. LIVE CLOCK & DYNAMIC GREETING
   ========================================== */
function initLiveClock() {
    const clockDisplay = document.getElementById('liveClockDisplay');
    const greetingDisplay = document.getElementById('greetingTime');

    function updateTime() {
        const now = new Date();

        if (greetingDisplay) {
            const hours = now.getHours();
            if (hours < 12) {
                greetingDisplay.textContent = 'Good Morning';
            } else if (hours < 17) {
                greetingDisplay.textContent = 'Good Afternoon';
            } else {
                greetingDisplay.textContent = 'Good Evening';
            }
        }

        if (clockDisplay) {
            let hours = now.getHours();
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12 || 12;
            const timeStr = `${String(hours).padStart(2, '0')}:${minutes}:${seconds} ${ampm}`;
            clockDisplay.textContent = timeStr;
        }
    }

    updateTime();
    setInterval(updateTime, 1000);
}

/* ==========================================
   5. STUDENT: PERSONAL TASK FORM & ACTIONS
   ========================================== */
function initTaskForm() {
    const addTaskForm = document.getElementById('addTaskForm');
    if (!addTaskForm) return;

    // Default task_date field to today's date if empty
    const dateInput = document.getElementById('task_date');
    if (dateInput && !dateInput.value) {
        const todayStr = new Date().toISOString().split('T')[0];
        dateInput.value = todayStr;
    }

    addTaskForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const title = document.getElementById('task_title')?.value.trim();
        const date = document.getElementById('task_date')?.value || new Date().toISOString().split('T')[0];
        const startVal = document.getElementById('task_start')?.value.trim() || '05:00';
        const startAmpm = document.getElementById('task_start_ampm')?.value || 'PM';
        const endVal = document.getElementById('task_end')?.value.trim() || '06:00';
        const endAmpm = document.getElementById('task_end_ampm')?.value || 'PM';

        if (!title) {
            showToast('Please enter a task name.', 'warning');
            return;
        }

        const fullStartStr = `${startVal} ${startAmpm}`;
        const fullEndStr = `${endVal} ${endAmpm}`;

        const sMins = parseTimeMins(fullStartStr);
        const eMins = parseTimeMins(fullEndStr);

        if (eMins <= sMins) {
            showToast('End time must be after Start time.', 'warning');
            return;
        }

        const start = formatTime12h(fullStartStr);
        const end = formatTime12h(fullEndStr);

        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, date, start, end })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                showToast(data.message || 'Task created successfully!', 'success');
                addTaskForm.reset();
                if (dateInput) dateInput.value = new Date().toISOString().split('T')[0];
                const startAmpmEl = document.getElementById('task_start_ampm');
                if (startAmpmEl) startAmpmEl.value = 'PM';
                const endAmpmEl = document.getElementById('task_end_ampm');
                if (endAmpmEl) endAmpmEl.value = 'PM';
                const startEl = document.getElementById('task_start');
                if (startEl) startEl.value = '05:00';
                const endEl = document.getElementById('task_end');
                if (endEl) endEl.value = '06:00';

                // Switch to Total Tasks subtab
                const allTasksTabBtn = document.querySelector('[data-subtab="all-tasks-subview"]');
                if (allTasksTabBtn) allTasksTabBtn.click();

                refreshDashboardData();
            } else {
                showToast(data.message || 'Failed to create task.', 'error');
            }
        } catch (error) {
            console.error('Error adding task:', error);
            showToast('An unexpected error occurred.', 'error');
        }
    });
}

function initTaskActions() {
    const tasksContainer = document.getElementById('tasksListContainer');
    if (!tasksContainer) return;

    tasksContainer.addEventListener('click', async (e) => {
        const toggleBtn = e.target.closest('.btn-toggle-task');
        const editBtn = e.target.closest('.btn-edit-task');
        const deleteBtn = e.target.closest('.btn-delete-task');

        if (toggleBtn) {
            const taskId = toggleBtn.getAttribute('data-task-id');
            if (taskId) await toggleTaskStatus(taskId);
        } else if (editBtn) {
            const taskId = editBtn.getAttribute('data-task-id');
            const title = editBtn.getAttribute('data-title');
            const date = editBtn.getAttribute('data-date');
            const start = editBtn.getAttribute('data-start');
            const end = editBtn.getAttribute('data-end');
            openEditTaskModal(taskId, title, date, start, end);
        } else if (deleteBtn) {
            const taskId = deleteBtn.getAttribute('data-task-id');
            if (taskId && confirm('Are you sure you want to delete this personal task?')) {
                await deleteTask(taskId);
            }
        }
    });
}

function initTaskEditModal() {
    const editModal = document.getElementById('editTaskModal');
    const editForm = document.getElementById('editTaskForm');
    const closeBtn = document.getElementById('btnCloseEditModal');
    const cancelBtn = document.getElementById('btnCancelEditTask');

    if (!editModal || !editForm) return;

    function closeModal() {
        editModal.style.display = 'none';
    }

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

    editForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const taskId = document.getElementById('editTaskId')?.value;
        const title = document.getElementById('editTaskTitle')?.value.trim();
        const date = document.getElementById('editTaskDate')?.value;
        const startVal = document.getElementById('editTaskStart')?.value.trim() || '05:00';
        const startAmpm = document.getElementById('editTaskStartAmpm')?.value || 'PM';
        const endVal = document.getElementById('editTaskEnd')?.value.trim() || '06:00';
        const endAmpm = document.getElementById('editTaskEndAmpm')?.value || 'PM';

        if (!title) {
            showToast('Task name is required.', 'warning');
            return;
        }

        const fullStartStr = `${startVal} ${startAmpm}`;
        const fullEndStr = `${endVal} ${endAmpm}`;

        const sMins = parseTimeMins(fullStartStr);
        const eMins = parseTimeMins(fullEndStr);

        if (eMins <= sMins) {
            showToast('End time must be after Start time.', 'warning');
            return;
        }

        const start = formatTime12h(fullStartStr);
        const end = formatTime12h(fullEndStr);

        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, date, start, end })
            });

            const data = await response.json();
            if (response.ok && data.success) {
                showToast(data.message || 'Task updated successfully.', 'success');
                closeModal();
                refreshDashboardData();
            } else {
                showToast(data.message || 'Failed to update task.', 'error');
            }
        } catch (error) {
            console.error('Error updating task:', error);
            showToast('Failed to update task.', 'error');
        }
    });
}

function openEditTaskModal(id, title, date, start, end) {
    const modal = document.getElementById('editTaskModal');
    if (!modal) return;
    document.getElementById('editTaskId').value = id || '';
    document.getElementById('editTaskTitle').value = title || '';
    document.getElementById('editTaskDate').value = date || new Date().toISOString().split('T')[0];

    const startParts = formatTime12hParts(start || '05:00 PM');
    const endParts = formatTime12hParts(end || '06:00 PM');

    const editStartEl = document.getElementById('editTaskStart');
    const editStartAmpmEl = document.getElementById('editTaskStartAmpm');
    const editEndEl = document.getElementById('editTaskEnd');
    const editEndAmpmEl = document.getElementById('editTaskEndAmpm');

    if (editStartEl) editStartEl.value = startParts.time;
    if (editStartAmpmEl) editStartAmpmEl.value = startParts.period;
    if (editEndEl) editEndEl.value = endParts.time;
    if (editEndAmpmEl) editEndAmpmEl.value = endParts.period;

    modal.style.display = 'flex';
}

async function toggleTaskStatus(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/toggle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        if (response.ok && data.success) {
            showToast(data.message || 'Task status updated.', 'info');
            refreshDashboardData();
        } else {
            showToast(data.message || 'Failed to update task status.', 'error');
        }
    } catch (error) {
        console.error('Error toggling task status:', error);
        showToast('Failed to update task status.', 'error');
    }
}

async function deleteTask(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        if (response.ok && data.success) {
            showToast(data.message || 'Task deleted.', 'info');
            refreshDashboardData();
        } else {
            showToast(data.message || 'Failed to delete task.', 'error');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showToast('Failed to delete task.', 'error');
    }
}

/* ==========================================
   6. STUDENT: DAY FILTER FOR TODAY TIMETABLE
   ========================================== */
function initStudentDayFilter() {
    const daySelect = document.getElementById('dayFilterSelect');
    if (!daySelect) return;

    daySelect.addEventListener('change', async () => {
        const selectedDay = daySelect.value;
        const titleEl = document.getElementById('selectedDayTitle');
        if (titleEl) titleEl.textContent = selectedDay;

        try {
            const res = await fetch(`/api/timetable/today?day=${encodeURIComponent(selectedDay)}`);
            if (!res.ok) return;
            const data = await res.json();

            const tbody = document.querySelector('#oneDayTable tbody');
            if (!tbody) return;

            if (!data.entries || !data.entries.length) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-muted text-center">No timetable available for ${escapeHtml(selectedDay)}.</td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = data.entries.map(item => {
                const isLib = item.type === 'Library';
                const subjectText = isLib && !item.subject.startsWith('📚') ? `📚 ${item.subject}` : item.subject;
                const typeText = isLib ? '📚 Library' : item.type;
                return `
                <tr class="row-status-${item.status.toLowerCase()} ${isLib ? 'row-library' : ''}">
                    <td><span class="badge-status badge-${item.status.toLowerCase()}">${escapeHtml(item.status)}</span></td>
                    <td><strong>${escapeHtml(formatTime12h(item.start))} - ${escapeHtml(formatTime12h(item.end))}</strong></td>
                    <td><strong>${escapeHtml(subjectText)}</strong></td>
                    <td>${escapeHtml(item.teacher || '-')}</td>
                    <td><span class="type-pill pill-${item.type.toLowerCase()}">${escapeHtml(typeText)}</span></td>
                </tr>
                `;
            }).join('');

        } catch (error) {
            console.error('Error fetching today timetable for day:', error);
        }
    });
}

/* ==========================================
   7. ADMIN: MANUAL TIMETABLE BUILDER
   ========================================== */
let adminWeeklySchedule = {
    'Monday': [],
    'Tuesday': [],
    'Wednesday': [],
    'Thursday': [],
    'Friday': []
};

function initAdminTimetable() {
    const entryForm = document.getElementById('ttEntryForm');
    const classForm = document.getElementById('classSelectorForm');
    const publishBtn = document.getElementById('btnPublishTt');
    if (!entryForm && !classForm) return;

    // Load initial class timetable
    loadClassTimetable();

    // Class selection change event
    ['selCourse', 'selYear', 'selSection'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('change', loadClassTimetable);
    });

    // Helper: Clear form errors
    function clearFormErrors() {
        const invalidInputs = entryForm ? entryForm.querySelectorAll('.is-invalid') : [];
        invalidInputs.forEach(el => el.classList.remove('is-invalid'));

        const errorMsgs = entryForm ? entryForm.querySelectorAll('.field-error-message') : [];
        errorMsgs.forEach(el => {
            el.textContent = '';
            el.classList.remove('active');
        });
    }

    // Helper: Show field error directly below input
    function showFieldError(fieldId, message) {
        let inputEl = document.getElementById(fieldId);
        if (!inputEl) return;

        inputEl.classList.add('is-invalid');

        // Find or target error element ID
        let errorEl = document.getElementById(`error-${fieldId}`);
        if (!errorEl) {
            const formGroup = inputEl.closest('.form-group');
            if (formGroup) {
                errorEl = formGroup.querySelector('.field-error-message');
            }
        }

        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.add('active');
        }
    }

    // Attach real-time error clearing on input/change
    if (entryForm) {
        ['entryDay', 'entryType', 'entrySubject', 'entryTeacher', 'entryStart', 'entryStartAmpm', 'entryEnd', 'entryEndAmpm'].forEach(id => {
            const inputEl = document.getElementById(id);
            if (inputEl) {
                inputEl.addEventListener('input', () => {
                    inputEl.classList.remove('is-invalid');
                    const errorEl = document.getElementById(`error-${id}`) || inputEl.closest('.form-group')?.querySelector('.field-error-message');
                    if (errorEl) {
                        errorEl.textContent = '';
                        errorEl.classList.remove('active');
                    }
                });
                inputEl.addEventListener('change', () => {
                    inputEl.classList.remove('is-invalid');
                    const errorEl = document.getElementById(`error-${id}`) || inputEl.closest('.form-group')?.querySelector('.field-error-message');
                    if (errorEl) {
                        errorEl.textContent = '';
                        errorEl.classList.remove('active');
                    }
                });
            }
        });
    }

    // Slot type change auto-adjusts lab duration to 2 hours
    const typeSelect = document.getElementById('entryType');
    const startInput = document.getElementById('entryStart');
    const startAmpmSelect = document.getElementById('entryStartAmpm');
    const endInput = document.getElementById('entryEnd');
    const endAmpmSelect = document.getElementById('entryEndAmpm');

    if (typeSelect && startInput && endInput) {
        typeSelect.addEventListener('change', () => {
            if (typeSelect.value === 'Lab') {
                adjustLabEndTime();
            }
        });
        startInput.addEventListener('change', () => {
            if (typeSelect.value === 'Lab') {
                adjustLabEndTime();
            }
        });
        if (startAmpmSelect) {
            startAmpmSelect.addEventListener('change', () => {
                if (typeSelect.value === 'Lab') {
                    adjustLabEndTime();
                }
            });
        }
    }

    function adjustLabEndTime() {
        if (!startInput.value) return;
        const startAmpm = startAmpmSelect ? startAmpmSelect.value : 'AM';
        const fullStartStr = `${startInput.value.trim()} ${startAmpm}`;
        const sMins = parseTimeMins(fullStartStr);
        const eMins = (sMins + 120) % (24 * 60);

        const parts = formatTime12hMins(eMins);
        endInput.value = parts.time;
        if (endAmpmSelect) {
            endAmpmSelect.value = parts.period;
        }
    }

    // Add / Edit Entry form submission
    if (entryForm) {
        entryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearFormErrors();

            const editId = document.getElementById('editEntryId').value;
            const day = document.getElementById('entryDay').value;
            const type = document.getElementById('entryType').value;
            const subject = document.getElementById('entrySubject').value.trim();
            const teacher = document.getElementById('entryTeacher').value.trim();

            const startVal = document.getElementById('entryStart').value.trim();
            const startAmpm = document.getElementById('entryStartAmpm')?.value || 'AM';
            const endVal = document.getElementById('entryEnd').value.trim();
            const endAmpm = document.getElementById('entryEndAmpm')?.value || 'AM';

            let hasClientError = false;

            let finalSubject = subject;
            if (!finalSubject) {
                if (type === 'Library') {
                    finalSubject = 'Library / Reading Time';
                } else {
                    showFieldError('entrySubject', 'Subject name is required.');
                    hasClientError = true;
                }
            }

            if (type !== 'Break' && type !== 'Library' && !teacher) {
                showFieldError('entryTeacher', 'Teacher name is required.');
                hasClientError = true;
            }

            if (!startVal) {
                showFieldError('entryStart', 'Start time is required.');
                hasClientError = true;
            }

            if (!endVal) {
                showFieldError('entryEnd', 'End time is required.');
                hasClientError = true;
            }

            const startStr = `${startVal} ${startAmpm}`;
            const endStr = `${endVal} ${endAmpm}`;
            const sMins = parseTimeMins(startStr);
            const eMins = parseTimeMins(endStr);

            if (startVal && endVal) {
                if (eMins <= sMins) {
                    showFieldError('entryEnd', 'End time must be after start time.');
                    hasClientError = true;
                } else if (type === 'Lab') {
                    const duration = eMins - sMins;
                    if (duration !== 120) {
                        showFieldError('entryEnd', 'Duration does not match the selected time range (Labs must be 2 hours).');
                        hasClientError = true;
                    }
                }
            }

            if (hasClientError) {
                const firstInvalid = entryForm.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                return;
            }

            const entry = {
                id: editId || 'entry_' + Date.now(),
                day,
                type,
                subject: finalSubject,
                teacher,
                start: startStr,
                end: endStr
            };

            const currentDayEntries = adminWeeklySchedule[day] || [];

            // Client/Server validation
            try {
                const valRes = await fetch('/admin/api/timetable/validate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        entry,
                        day_entries: currentDayEntries,
                        edit_entry_id: editId
                    })
                });

                const valData = await valRes.json();

                if (!valData.success) {
                    const errs = valData.errors || {};
                    let focused = false;

                    if (errs.subject) {
                        showFieldError('entrySubject', errs.subject);
                        focused = true;
                    }
                    if (errs.teacher) {
                        showFieldError('entryTeacher', errs.teacher);
                        focused = true;
                    }
                    if (errs.start) {
                        showFieldError('entryStart', errs.start);
                        focused = true;
                    }
                    if (errs.end) {
                        showFieldError('entryEnd', errs.end);
                        focused = true;
                    }
                    if (errs.type && !errs.end) {
                        showFieldError('entryType', errs.type);
                        focused = true;
                    }
                    if (errs.general) {
                        showToast(errs.general, 'error');
                    }

                    const firstInvalid = entryForm.querySelector('.is-invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                    return;
                }

                // Append or replace entry in local draft schedule
                if (editId) {
                    // Remove entry from any day list first if day changed
                    Object.keys(adminWeeklySchedule).forEach(d => {
                        if (Array.isArray(adminWeeklySchedule[d])) {
                            adminWeeklySchedule[d] = adminWeeklySchedule[d].filter(item => String(item.id) !== String(editId));
                        }
                    });
                    if (!adminWeeklySchedule[day]) adminWeeklySchedule[day] = [];
                    adminWeeklySchedule[day].push(entry);
                } else {
                    if (!adminWeeklySchedule[day]) adminWeeklySchedule[day] = [];
                    adminWeeklySchedule[day].push(entry);
                }

                // Sort day entries by start time
                adminWeeklySchedule[day].sort((a, b) => {
                    const aMin = parseTimeMins(a.start);
                    const bMin = parseTimeMins(b.start);
                    return aMin - bMin;
                });

                renderAdminPreviewGrid();
                resetEntryForm();
                showToast(`Entry added to preview for ${day} (${startStr}-${endStr})`, 'success');

                // Auto-save draft
                autoSaveDraft();

            } catch (error) {
                console.error('Validation error:', error);
                showToast('Failed to validate entry.', 'error');
            }
        });
    }

    const cancelEditBtn = document.getElementById('btnCancelEdit');
    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', resetEntryForm);
    }

    // Publish button handler
    if (publishBtn) {
        publishBtn.addEventListener('click', async () => {
            const course = document.getElementById('selCourse')?.value;
            const department = document.getElementById('selDepartment')?.value;
            const year = document.getElementById('selYear')?.value;
            const section = document.getElementById('selSection')?.value;

            // Check if any day has entries
            let totalEntries = 0;
            Object.values(adminWeeklySchedule).forEach(list => totalEntries += list.length);

            if (totalEntries === 0) {
                if (!confirm('The weekly timetable is currently empty. Do you want to publish an empty timetable?')) {
                    return;
                }
            }

            const originalBtnHtml = publishBtn.innerHTML;
            publishBtn.disabled = true;
            publishBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Publishing...';

            try {
                const response = await fetch('/admin/api/timetable/publish', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        course,
                        department,
                        year,
                        section,
                        weekly_schedule: adminWeeklySchedule
                    })
                });

                const data = await response.json();
                if (response.ok && data.success) {
                    showToast('Timetable published successfully ✓', 'success');
                    const badge = document.getElementById('ttStatusBadge');
                    if (badge) {
                        badge.textContent = 'Status: Published (Active)';
                        badge.className = 'status-pill status-live';
                    }
                } else {
                    showToast(data.message || 'Failed to publish timetable.', 'error');
                }
            } catch (error) {
                console.error('Error publishing timetable:', error);
                showToast('Failed to publish timetable.', 'error');
            } finally {
                publishBtn.disabled = false;
                publishBtn.innerHTML = originalBtnHtml;
            }
        });
    }
}

async function loadClassTimetable() {
    const course = document.getElementById('selCourse')?.value || 'B.Tech CS';
    const department = document.getElementById('selDepartment')?.value || 'Computer Science & Technology';
    const year = document.getElementById('selYear')?.value || '3rd Year';
    const section = document.getElementById('selSection')?.value || 'Section A';

    try {
        const res = await fetch(`/admin/api/timetable/load?course=${encodeURIComponent(course)}&department=${encodeURIComponent(department)}&year=${encodeURIComponent(year)}&section=${encodeURIComponent(section)}`);
        if (!res.ok) return;
        const data = await res.json();

        if (data.success && data.timetable) {
            adminWeeklySchedule = data.timetable.weekly_schedule || {
                'Monday': [], 'Tuesday': [], 'Wednesday': [], 'Thursday': [], 'Friday': [], 'Saturday': []
            };

            const badge = document.getElementById('ttStatusBadge');
            if (badge) {
                const status = data.timetable.status;
                if (status === 'published') {
                    badge.textContent = 'Status: Published (Active)';
                    badge.className = 'status-pill status-live';
                } else {
                    badge.textContent = 'Status: Draft';
                    badge.className = 'status-pill status-draft';
                }
            }
            renderAdminPreviewGrid();
        }
    } catch (error) {
        console.error('Error loading class timetable:', error);
    }
}

async function autoSaveDraft() {
    const course = document.getElementById('selCourse')?.value;
    const department = document.getElementById('selDepartment')?.value;
    const year = document.getElementById('selYear')?.value;
    const section = document.getElementById('selSection')?.value;

    try {
        await fetch('/admin/api/timetable/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                course,
                department,
                year,
                section,
                weekly_schedule: adminWeeklySchedule
            })
        });
    } catch (err) {
        console.error('Auto-save draft error:', err);
    }
}

function renderAdminPreviewGrid() {
    const container = document.getElementById('previewDaysContainer');
    if (!container) return;

    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

    container.innerHTML = days.map(day => {
        const entries = adminWeeklySchedule[day] || [];
        return `
            <div class="day-preview-card">
                <div class="day-card-header">
                    <h4>${escapeHtml(day)}</h4>
                    <span class="count-badge">${entries.length} slots</span>
                </div>
                <div class="day-card-body">
                    ${entries.length ? `
                        <table class="table preview-grid-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Subject</th>
                                    <th>Teacher</th>
                                    <th>Type</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${entries.map(lec => {
                                    const isLib = lec.type === 'Library';
                                    const subjectText = isLib && !lec.subject.startsWith('📚') ? `📚 ${lec.subject}` : lec.subject;
                                    const typeText = isLib ? '📚 Library' : lec.type;
                                    return `
                                    <tr class="row-${lec.type.toLowerCase()}">
                                        <td class="time-col"><strong>${escapeHtml(formatTime12h(lec.start))} - ${escapeHtml(formatTime12h(lec.end))}</strong></td>
                                        <td><strong>${escapeHtml(subjectText)}</strong></td>
                                        <td>${escapeHtml(lec.teacher || '-')}</td>
                                        <td><span class="type-pill pill-${lec.type.toLowerCase()}">${escapeHtml(typeText)}</span></td>
                                        <td class="action-cell">
                                            <button type="button" class="btn-sm-edit" onclick="editAdminEntry('${day}', '${lec.id}')" title="Edit Entry">
                                                <i class="fa-solid fa-pen"></i>
                                            </button>
                                            <button type="button" class="btn-sm-delete" onclick="deleteAdminEntry('${day}', '${lec.id}')" title="Delete Entry">
                                                <i class="fa-solid fa-trash-can"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    ` : `
                        <div class="empty-day-state">
                            <p class="text-muted">No slots added for ${day}.</p>
                        </div>
                    `}
                </div>
            </div>
        `;
    }).join('');
}

function editAdminEntry(day, entryId) {
    const list = adminWeeklySchedule[day] || [];
    const target = list.find(item => String(item.id) === String(entryId));
    if (!target) return;

    document.getElementById('editEntryId').value = target.id;
    document.getElementById('entryDay').value = day;
    document.getElementById('entryType').value = target.type || 'Lecture';
    document.getElementById('entrySubject').value = target.subject || '';
    document.getElementById('entryTeacher').value = target.teacher || '';

    const startObj = formatTime12hParts(target.start || '09:00 AM');
    const endObj = formatTime12hParts(target.end || '10:00 AM');

    document.getElementById('entryStart').value = startObj.time;
    if (document.getElementById('entryStartAmpm')) {
        document.getElementById('entryStartAmpm').value = startObj.period;
    }

    document.getElementById('entryEnd').value = endObj.time;
    if (document.getElementById('entryEndAmpm')) {
        document.getElementById('entryEndAmpm').value = endObj.period;
    }

    const titleEl = document.getElementById('formSectionTitle');
    if (titleEl) titleEl.innerHTML = `<i class="fa-solid fa-pen"></i> Edit Timetable Entry (${day})`;

    const saveBtn = document.getElementById('btnSaveEntry');
    if (saveBtn) saveBtn.innerHTML = `<i class="fa-solid fa-check"></i> Save Entry Changes`;

    const cancelBtn = document.getElementById('btnCancelEdit');
    if (cancelBtn) cancelBtn.style.display = 'inline-block';

    document.getElementById('ttEntryForm').scrollIntoView({ behavior: 'smooth' });
}

function deleteAdminEntry(day, entryId) {
    if (!confirm(`Are you sure you want to remove this timetable slot from ${day}?`)) return;
    if (adminWeeklySchedule[day]) {
        adminWeeklySchedule[day] = adminWeeklySchedule[day].filter(item => String(item.id) !== String(entryId));
        renderAdminPreviewGrid();
        autoSaveDraft();
        showToast(`Slot removed from ${day}.`, 'info');
    }
}

function resetEntryForm() {
    const form = document.getElementById('ttEntryForm');
    if (form) {
        form.reset();
        const invalidInputs = form.querySelectorAll('.is-invalid');
        invalidInputs.forEach(el => el.classList.remove('is-invalid'));

        const errorMsgs = form.querySelectorAll('.field-error-message');
        errorMsgs.forEach(el => {
            el.textContent = '';
            el.classList.remove('active');
        });
    }
    document.getElementById('editEntryId').value = '';
    document.getElementById('entryStart').value = '09:00';
    if (document.getElementById('entryStartAmpm')) document.getElementById('entryStartAmpm').value = 'AM';
    document.getElementById('entryEnd').value = '10:00';
    if (document.getElementById('entryEndAmpm')) document.getElementById('entryEndAmpm').value = 'AM';

    const titleEl = document.getElementById('formSectionTitle');
    if (titleEl) titleEl.innerHTML = `<i class="fa-solid fa-plus-circle"></i> Add Timetable Slot Entry`;

    const saveBtn = document.getElementById('btnSaveEntry');
    if (saveBtn) saveBtn.innerHTML = `<i class="fa-solid fa-plus"></i> Add Entry to Preview`;

    const cancelBtn = document.getElementById('btnCancelEdit');
    if (cancelBtn) cancelBtn.style.display = 'none';
}

function str(val) {
    return String(val || '');
}

function parseTimeMins(timeStr) {
    if (!timeStr) return 0;
    const str = String(timeStr).trim();
    const isPm = /PM/i.test(str);
    const isAm = /AM/i.test(str);
    const cleaned = str.replace(/[^0-9:]/g, '');
    const parts = cleaned.split(':');
    if (!parts.length || !parts[0]) return 0;

    let hours = parseInt(parts[0], 10) || 0;
    const minutes = parts.length > 1 ? (parseInt(parts[1], 10) || 0) : 0;

    if (isPm) {
        if (hours < 12) hours += 12;
    } else if (isAm) {
        if (hours === 12) hours = 0;
    }

    return hours * 60 + minutes;
}

function formatTime12h(timeStr) {
    if (!timeStr) return '';
    const mins = parseTimeMins(timeStr);
    let hours = Math.floor(mins / 60) % 24;
    const minutes = mins % 60;
    const period = hours < 12 ? 'AM' : 'PM';
    hours = hours % 12;
    if (hours === 0) hours = 12;
    const hStr = String(hours).padStart(2, '0');
    const mStr = String(minutes).padStart(2, '0');
    return `${hStr}:${mStr} ${period}`;
}

function formatTime12hMins(mins) {
    let hours = Math.floor(mins / 60) % 24;
    const minutes = mins % 60;
    const period = hours < 12 ? 'AM' : 'PM';
    hours = hours % 12;
    if (hours === 0) hours = 12;
    const hStr = String(hours).padStart(2, '0');
    const mStr = String(minutes).padStart(2, '0');
    return { time: `${hStr}:${mStr}`, period: period };
}

function formatTime12hParts(timeStr) {
    const mins = parseTimeMins(timeStr);
    return formatTime12hMins(mins);
}

function formatTime24h(timeStr) {
    if (!timeStr) return '00:00';
    const mins = parseTimeMins(timeStr);
    const hours = Math.floor(mins / 60) % 24;
    const minutes = mins % 60;
    const hStr = String(hours).padStart(2, '0');
    const mStr = String(minutes).padStart(2, '0');
    return `${hStr}:${mStr}`;
}

/* ==========================================
   8. DYNAMIC DASHBOARD REFRESH
   ========================================== */
async function refreshDashboardData() {
    try {
        const response = await fetch('/api/dashboard-data');
        if (!response.ok) return;

        const data = await response.json();
        
        updateMetrics(data.overview);
        renderTasksList(data.personal_tasks);
        renderTimeline(data.timeline);
        updateHeroCards(data.current_activity, data.next_up);

        const countHeader = document.getElementById('totalTasksCountHeader');
        if (countHeader) countHeader.textContent = data.overview.total_tasks;

    } catch (error) {
        console.error('Error refreshing dashboard data:', error);
    }
}

function updateMetrics(overview) {
    if (!overview) return;
    const cards = document.querySelectorAll('.overview-metrics-grid .metric-card');
    cards.forEach(card => {
        const label = card.querySelector('.metric-label')?.textContent || '';
        const valEl = card.querySelector('.metric-value');
        if (!valEl) return;

        if (label.includes('Total Lectures')) valEl.textContent = overview.total_lectures;
        else if (label.includes('Completed Lectures')) valEl.textContent = overview.completed_lectures;
        else if (label.includes('Remaining Lectures')) valEl.textContent = overview.remaining_lectures;
        else if (label.includes('Total Personal Tasks')) valEl.textContent = overview.total_tasks;
        else if (label.includes('Pending Tasks')) valEl.textContent = overview.pending_tasks;
    });

    const tasksTabBtn = document.querySelector('[data-subtab="all-tasks-subview"]');
    if (tasksTabBtn) {
        tasksTabBtn.textContent = `Total Tasks (${overview.total_tasks})`;
    }
}

function renderTasksList(tasks) {
    const container = document.getElementById('tasksListContainer');
    if (!container) return;

    if (!tasks || !tasks.length) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fa-regular fa-clipboard"></i>
                <p>No personal tasks found. Click "+ Add Task" to create your first task!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = tasks.map(task => `
        <div class="task-card ${task.completed ? 'task-completed' : ''}" data-task-id="${task.id}">
            <div class="task-card-header">
                <span class="date-chip"><i class="fa-regular fa-calendar"></i> ${escapeHtml(task.date)}</span>
                <span class="status-badge-sm ${task.completed ? 'completed' : 'pending'}">
                    ${task.completed ? 'Completed' : 'Pending'}
                </span>
            </div>
            <h4 class="task-title">${escapeHtml(task.title)}</h4>
            <div class="task-card-footer">
                <span class="task-time"><i class="fa-regular fa-clock"></i> ${escapeHtml(task.start)} - ${escapeHtml(task.end)}</span>
                <div class="task-actions">
                    <button type="button" class="btn-toggle-task" data-task-id="${task.id}" title="Toggle Completion">
                        <i class="fa-solid ${task.completed ? 'fa-circle-check color-success' : 'fa-circle color-warning'}"></i>
                    </button>
                    <button type="button" class="btn-edit-task" data-task-id="${task.id}" data-title="${escapeHtml(task.title)}" data-date="${escapeHtml(task.date)}" data-start="${escapeHtml(task.start)}" data-end="${escapeHtml(task.end)}" title="Change Task">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button type="button" class="btn-delete-task" data-task-id="${task.id}" title="Delete Task">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function renderTimeline(timeline) {
    const container = document.querySelector('.timeline-container');
    if (!container) return;

    if (!timeline || !timeline.length) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fa-regular fa-calendar-xmark"></i>
                <p>No timetable available</p>
            </div>
        `;
        return;
    }

    const itemsHtml = timeline.map(item => `
        <div class="timeline-item item-${item.status.toLowerCase()} item-${item.item_type}">
            <div class="timeline-time">
                <span class="start-t">${escapeHtml(item.start)}</span>
                <span class="dash-sep">-</span>
                <span class="end-t">${escapeHtml(item.end)}</span>
            </div>
            <div class="timeline-marker">
                <div class="marker-dot"></div>
                <div class="marker-line"></div>
            </div>
            <div class="timeline-content">
                <div class="item-header">
                    <h4 class="item-title">${escapeHtml(item.title)}</h4>
                    <span class="badge-status badge-${item.status.toLowerCase()}">
                        ${item.status === 'Completed' ? '<i class="fa-solid fa-check"></i> Completed' :
                          item.status === 'Current' || item.status === 'LIVE NOW' ? '<i class="fa-solid fa-satellite-dish"></i> LIVE NOW' :
                          '<i class="fa-regular fa-clock"></i> Upcoming'}
                    </span>
                </div>
                <p class="item-subtitle">${escapeHtml(item.subtitle)}</p>
            </div>
        </div>
    `).join('');

    container.innerHTML = `<div class="timeline-list">${itemsHtml}</div>`;
}

function updateHeroCards(current, next) {
    if (current) {
        const curTitle = document.getElementById('currentActivityTitle');
        const curSub = document.getElementById('currentActivitySubtitle');
        const curStart = document.getElementById('currentStartTime');
        const curEnd = document.getElementById('currentEndTime');
        const curRem = document.getElementById('currentRemTimeStr');

        if (curTitle) curTitle.textContent = current.title;
        if (curSub) curSub.textContent = current.subtitle;
        if (curStart) curStart.textContent = current.start;
        if (curEnd) curEnd.textContent = current.end;
        if (curRem) curRem.textContent = current.remaining_str;
    }

    if (next) {
        const nextTitle = document.getElementById('nextUpTitle');
        const nextSub = document.getElementById('nextUpSubtitle');
        const nextUntil = document.getElementById('nextUpUntilStr');

        if (nextTitle) nextTitle.textContent = next.title;
        if (nextSub) nextSub.textContent = next.subtitle;
        if (nextUntil) nextUntil.textContent = next.time_until_str;
    }
}

/* Helper Utilities */
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function showToast(message, type = 'info') {
    let container = document.querySelector('.flash-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-container';
        document.body.prepend(container);
    }

    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'warning' : type}`;
    
    let iconClass = 'fa-circle-info';
    if (type === 'success') iconClass = 'fa-circle-check';
    if (type === 'warning' || type === 'error') iconClass = 'fa-triangle-exclamation';

    toast.innerHTML = `
        <i class="fa-solid ${iconClass}"></i>
        <span>${escapeHtml(message)}</span>
        <button class="close-alert" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 4000);
}

