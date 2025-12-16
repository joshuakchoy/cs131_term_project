
from flask import Blueprint, render_template, flash, redirect, url_for, current_app, send_from_directory, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from ..forms import CreateAssignmentForm, CreateCourseForm, EnrollStudentForm, SubmitAssignmentForm, ComposeMessageForm, AnnouncementForm, AssignTAForm, GradeSubmissionForm
from ..models import db, Assignment, Course, User, Enrollment, Submission, Message, Announcement, TAAssignment

bp = Blueprint("main", __name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

@bp.route("/")
@login_required
def default():
    return redirect(url_for("auth.login"))

@bp.route("/home")
@login_required
def index():
    if current_user.role == 'student':
        # Get course IDs the student is enrolled in
        enrolled_course_ids = [enrollment.course_id for enrollment in current_user.courses_enrolled]
        # Filter assignments to only those courses
        assignments = Assignment.query.filter(Assignment.course_id.in_(enrolled_course_ids)).order_by(Assignment.due_date).all()
    elif current_user.role == 'instructor':
        # Instructors see assignments from courses they teach
        taught_course_ids = [course.id for course in current_user.courses_taught]
        assignments = Assignment.query.filter(Assignment.course_id.in_(taught_course_ids)).order_by(Assignment.due_date).all()
    else:  # TA
        # TAs see assignments from courses they are assigned to
        ta_course_ids = [ta_assignment.course_id for ta_assignment in current_user.ta_assignments]
        assignments = Assignment.query.filter(Assignment.course_id.in_(ta_course_ids)).order_by(Assignment.due_date).all()
    
    return render_template("main/home.html", assignments=assignments)

@bp.route("/grades")
@login_required
def grades():
    if current_user.role == "instructor":
        # Show courses taught by this instructor
        courses = Course.query.filter_by(teacher=current_user.id).all()
        course_averages = {}
    elif current_user.role == "student":
        # Show courses enrolled by this student
        enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
        courses = [e.course for e in enrollments]
        
        # Calculate average grade for each course
        course_averages = {}
        for course in courses:
            # Get all assignments for this course
            assignments = Assignment.query.filter_by(course_id=course.id).all()
            assignment_ids = [a.id for a in assignments]
            
            # Get student's graded submissions for this course
            graded_submissions = Submission.query.filter(
                Submission.student_id == current_user.id,
                Submission.assignment_id.in_(assignment_ids),
                Submission.grade.isnot(None)
            ).all()
            
            if graded_submissions:
                total = sum(sub.grade for sub in graded_submissions)
                average = round(total / len(graded_submissions), 1)
                course_averages[course.id] = average
            else:
                course_averages[course.id] = None
    else:  # TA
        # Show courses the TA is assigned to
        ta_assignments = TAAssignment.query.filter_by(ta_id=current_user.id).all()
        courses = [ta_assignment.course for ta_assignment in ta_assignments]
        course_averages = {}
    
    return render_template("main/grades.html", courses=courses, course_averages=course_averages)

@bp.route("/classes")
@login_required
def classes():
    if current_user.role == "instructor":
        # Show courses taught by this instructor
        courses = Course.query.filter_by(teacher=current_user.id).all()
    elif current_user.role == "student":
        # Show courses enrolled by this student
        enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
        courses = [e.course for e in enrollments]
    else:  # TA
        # Show courses the TA is assigned to
        ta_assignments = TAAssignment.query.filter_by(ta_id=current_user.id).all()
        courses = [ta_assignment.course for ta_assignment in ta_assignments]
    return render_template("main/classes.html", courses=courses)

@bp.route("/assignments")
@login_required
def assignments():
    # Server-side sorting support via query params: ?sort=due_date|course&order=asc|desc
    sort = request.args.get("sort")
    order = request.args.get("order", "asc")

    q = Assignment.query
    # If the current user is an authenticated student, only show assignments
    # for courses they are enrolled in. Instructors and anonymous users keep full view.
    if getattr(current_user, 'is_authenticated', False) and getattr(current_user, 'role', None) == 'student':
        enrolled = Enrollment.query.filter_by(student_id=current_user.id).all()
        enrolled_ids = [e.course_id for e in enrolled]
        # if student isn't enrolled anywhere, return empty list quickly
        if not enrolled_ids:
            return render_template("main/assignments.html", assignments=[], sort=sort, order=order)
        q = q.filter(Assignment.course_id.in_(enrolled_ids))
    if sort == "due_date":
        if order == "asc":
            q = q.order_by(Assignment.due_date.asc())
        else:
            q = q.order_by(Assignment.due_date.desc())
    elif sort == "course":
        # outerjoin so unlinked assignments are included
        q = q.outerjoin(Course)
        if order == "asc":
            q = q.order_by(Course.title.asc())
        else:
            q = q.order_by(Course.title.desc())
    else:
        # default order (newest first)
        q = q.order_by(Assignment.id.desc())

    assignments = q.all()
    
    # For students, check which assignments have been submitted
    submission_status = {}
    if getattr(current_user, 'is_authenticated', False) and getattr(current_user, 'role', None) == 'student':
        for assignment in assignments:
            existing_submission = Submission.query.filter_by(
                assignment_id=assignment.id,
                student_id=current_user.id
            ).first()
            submission_status[assignment.id] = existing_submission is not None
    
    return render_template("main/assignments.html", assignments=assignments, sort=sort, order=order, submission_status=submission_status)

@bp.route("/create_assignment", methods=["GET", "POST"])
@login_required
def create_assignment():
    # only instructors can create assignments
    if getattr(current_user, "role", None) != "instructor":
        flash("Access denied: instructors only.", "danger")
        return redirect(url_for("main.index"))

    form = CreateAssignmentForm()
    # Populate course choices with courses owned by the current user (instructor)
    courses = Course.query.filter_by(teacher=current_user.id).all()
    form.course_id.choices = [(c.id, c.title) for c in courses]

    if not form.course_id.choices:
        flash("You don't have any courses yet. Create a course first.", "info")

    if form.validate_on_submit():
        # convert date object to ISO string for storing in the String column
        due_val = form.due_date.data
        if hasattr(due_val, "strftime"):
            due_str = due_val.strftime("%Y-%m-%d")
        else:
            due_str = due_val

        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            due_date=due_str,
            assignment_type=form.assignment_type.data,
            course_id=form.course_id.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash("Assignment created successfully!", "success")
        return redirect(url_for("main.assignments"))
    return render_template("main/create_assignment.html", form=form)

@bp.route("/create_course", methods=["GET", "POST"])
@login_required
def create_course():
    # only instructors can create courses
    if getattr(current_user, "role", None) != "instructor":
        flash("Access denied: instructors only.", "danger")
        return redirect(url_for("main.index"))

    form = CreateCourseForm()

    if form.validate_on_submit():
        # Check if course code already exists
        existing = Course.query.filter_by(code=form.code.data).first()
        if existing:
            flash(f"Course code '{form.code.data}' already exists.", "danger")
            return render_template("main/create_course.html", form=form)
        
        course = Course(
            title=form.name.data,
            code=form.code.data,
            description=form.description.data,
            teacher=current_user.id,
            image_url=form.image_url.data or None
        )
        db.session.add(course)
        db.session.commit()
        flash("Course created successfully!", "success")
        return redirect(url_for("main.classes"))
    return render_template("main/create_course.html", form=form)

@bp.route("/analytics")
@login_required
def analytics():
    # Only students see personal analytics; others see a simple page
    if getattr(current_user, "role", None) != "student":
        return render_template("main/analytics.html", assignments_data=[], gpa=None)

    # Get courses the student is enrolled in
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    course_ids = [e.course_id for e in enrollments]
    courses = Course.query.filter(Course.id.in_(course_ids)).all() if course_ids else []

    assignments_data = []

    # Collect assignment-level analytics
    for course in courses:
        course_assignments = Assignment.query.filter_by(course_id=course.id).all()
        for assignment in course_assignments:
            subs = Submission.query.filter_by(assignment_id=assignment.id).all()
            grades = [s.grade for s in subs if s.grade is not None]

            # Student performance for this assignment
            stu_sub = next((s for s in subs if s.student_id == current_user.id), None)
            student_score = stu_sub.grade if (stu_sub and stu_sub.grade is not None) else None

            class_avg = round(sum(grades) / len(grades), 2) if grades else None
            high = max(grades) if grades else None
            low = min(grades) if grades else None

            assignments_data.append({
                "assignment_id": assignment.id,
                "assignment_title": assignment.title,
                "course_title": course.title,
                "student_score": student_score,
                "class_avg": class_avg,
                "high": high,
                "low": low,
            })

    # Compute GPA from all courses the student is enrolled in
    # Approach: average student's graded percentages per course -> map to 4.0 scale -> average
    def pct_to_gpa(pct):
        if pct is None:
            return None
        if pct >= 90:
            return 4.0
        if pct >= 80:
            return 3.0
        if pct >= 70:
            return 2.0
        if pct >= 60:
            return 1.0
        return 0.0

    course_gp_list = []
    for course in courses:
        course_assignment_ids = [a.id for a in Assignment.query.filter_by(course_id=course.id).all()]
        if not course_assignment_ids:
            continue
        stu_subs = Submission.query.filter(Submission.assignment_id.in_(course_assignment_ids), Submission.student_id == current_user.id).all()
        stu_grades = [s.grade for s in stu_subs if s.grade is not None]
        if not stu_grades:
            continue
        avg_pct = sum(stu_grades) / len(stu_grades)
        gp = pct_to_gpa(avg_pct)
        if gp is not None:
            course_gp_list.append(gp)

    gpa = round(sum(course_gp_list) / len(course_gp_list), 2) if course_gp_list else None

    return render_template("main/analytics.html", assignments_data=assignments_data, gpa=gpa)


@bp.route("/teacher_portal")
@login_required
def teacher_portal():
    # Only allow instructors to view the teacher portal
    if getattr(current_user, "role", None) != "instructor":
        flash("Access denied: instructor only.", "danger")
        return redirect(url_for("main.index"))
    
    # Get all students and courses taught by the instructor
    students = User.query.filter_by(role="student").all()
    courses = Course.query.filter_by(teacher=current_user.id).all()
    form = EnrollStudentForm()
    return render_template("main/teacher_portal.html", students=students, courses=courses, form=form)


@bp.route("/course/<int:course_id>") #specific course details
@login_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if user is the instructor of this course
    if course.teacher != current_user.id:
        flash("You do not have permission to view this course.", "danger")
        return redirect(url_for("main.classes"))
    
    # Get all enrolled students
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    students = [e.student for e in enrollments]
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    
    form = EnrollStudentForm()
    return render_template("main/view_course.html", course=course, students=students, assignments=assignments, form=form)


@bp.route("/course/<int:course_id>/enroll", methods=["POST"])
@login_required
def enroll_student(course_id):
    """Add a student/TA to a course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is the instructor of this course
    if course.teacher != current_user.id:
        flash("You do not have permission to modify this course.", "danger")
        return redirect(url_for("main.classes"))
    
    form = EnrollStudentForm()
    if form.validate_on_submit():
        # Find student/TA by username or email
        student = User.query.filter(
            (User.username == form.student_identifier.data) |
            (User.email == form.student_identifier.data)
        ).first()
        
        if student.role == "instructor":
            flash("User is not student/TA", "danger")
            return redirect(url_for("main.teacher_portal"))
        
        # Check if student is already enrolled
        existing = Enrollment.query.filter_by(student_id=student.id, course_id=course_id).first()
        if existing:
            flash(f"{student.username} is already enrolled in this course.", "info")
            return redirect(url_for("main.teacher_portal"))
        
        # Create enrollment
        enrollment = Enrollment(student_id=student.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        flash(f"{student.username} has been added to the course.", "success")
        return redirect(url_for("main.teacher_portal"))
    
    flash("Form validation failed.", "danger")
    return redirect(url_for("main.view_course", course_id=course_id))

@bp.route("/course/<int:course_id>/manage_tas", methods=["GET", "POST"])
@login_required
def manage_tas(course_id):
    """Manage TAs assigned to a course (instructor only)"""
    if current_user.role != 'instructor':
        flash("Only instructors can manage TAs.", "danger")
        return redirect(url_for("main.classes"))
    
    course = Course.query.get_or_404(course_id)
    
    # Check if user is the instructor of this course
    if course.teacher != current_user.id:
        flash("You do not have permission to manage TAs for this course.", "danger")
        return redirect(url_for("main.classes"))
    
    form = AssignTAForm()
    
    # Populate TA dropdown with all TAs
    form.ta_id.choices = [(ta.id, ta.username) for ta in User.query.filter_by(role='ta').all()]
    form.course_id.choices = [(course.id, course.title)]
    form.course_id.data = course.id
    
    if form.validate_on_submit():
        # Check if TA is already assigned
        existing = TAAssignment.query.filter_by(ta_id=form.ta_id.data, course_id=course_id).first()
        if existing:
            flash("This TA is already assigned to this course.", "info")
        else:
            # Create TA assignment
            ta_assignment = TAAssignment(ta_id=form.ta_id.data, course_id=course_id)
            db.session.add(ta_assignment)
            db.session.commit()
            ta = User.query.get(form.ta_id.data)
            flash(f"{ta.username} has been assigned as a TA for this course.", "success")
        return redirect(url_for("main.manage_tas", course_id=course_id))
    
    # Get currently assigned TAs
    ta_assignments = TAAssignment.query.filter_by(course_id=course_id).all()
    assigned_tas = [ta_assignment.ta for ta_assignment in ta_assignments]
    
    return render_template("main/manage_tas.html", course=course, assigned_tas=assigned_tas, ta_assignments=ta_assignments, form=form)

@bp.route("/course/<int:course_id>/remove_ta/<int:ta_id>", methods=["POST"])
@login_required
def remove_ta(course_id, ta_id):
    """Remove a TA from a course"""
    if current_user.role != 'instructor':
        flash("Only instructors can remove TAs.", "danger")
        return redirect(url_for("main.classes"))
    
    course = Course.query.get_or_404(course_id)
    
    # Check if user is the instructor of this course
    if course.teacher != current_user.id:
        flash("You do not have permission to modify this course.", "danger")
        return redirect(url_for("main.classes"))
    
    # Find and remove the TA assignment
    ta_assignment = TAAssignment.query.filter_by(ta_id=ta_id, course_id=course_id).first()
    if ta_assignment:
        db.session.delete(ta_assignment)
        db.session.commit()
        ta = User.query.get(ta_id)
        flash(f"{ta.username} has been removed as a TA from this course.", "success")
    else:
        flash("TA assignment not found.", "danger")
    
    return redirect(url_for("main.manage_tas", course_id=course_id))

@bp.route("/submit_assignment/<int:assignment_id>", methods=["GET", "POST"]) #lets you submit a PDF for an assignment
@login_required
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    form = SubmitAssignmentForm()
    
    if form.validate_on_submit():
        # Check if student already submitted
        existing = Submission.query.filter_by(
            assignment_id=assignment_id,
            student_id=current_user.id
        ).first()
        
        # Handle file upload
        file_path = None
        unique_filename = None
        if form.file.data:
            file = form.file.data
            filename = secure_filename(file.filename)
            # Create unique filename: userid_assignmentid_filename
            unique_filename = f"{current_user.id}_{assignment_id}_{filename}"
            
            # Ensure upload folder exists
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # Delete old file if resubmitting
            if existing and existing.file_path:
                old_file = os.path.join(upload_folder, existing.file_path)
                if os.path.exists(old_file):
                    os.remove(old_file)
        
        if existing:
            # Update existing submission (resubmit)
            existing.content = form.content.data
            if unique_filename:
                existing.file_path = unique_filename
            from datetime import datetime
            existing.submitted_at = datetime.utcnow()
            db.session.commit()
            flash("Assignment resubmitted successfully!", "success")
        else:
            # Create new submission
            submission = Submission(
                assignment_id=assignment_id,
                student_id=current_user.id,
                content=form.content.data,
                file_path=unique_filename if file_path else None
            )
            db.session.add(submission)
            db.session.commit()
            flash("Assignment submitted successfully!", "success")
        
        return redirect(url_for("main.assignments"))
    
    # Check if student already has a submission
    existing_submission = Submission.query.filter_by(
        assignment_id=assignment_id,
        student_id=current_user.id
    ).first()
    
    # Pre-populate form with existing submission data
    if existing_submission and not form.is_submitted():
        form.content.data = existing_submission.content
    
    return render_template("main/submit_assignment.html", form=form, assignment=assignment, existing_submission=existing_submission)

@bp.route("/download/<filename>")
@login_required
def download_file(filename):
    """Download submitted assignment file"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename, as_attachment=True)

@bp.route("/view_submissions/<int:assignment_id>")
@login_required
def view_submissions(assignment_id):
    """View all submissions for an assignment (instructors and TAs only)"""
    if current_user.role not in ["instructor", "ta"]:
        flash("Access denied: instructors and TAs only.", "danger")
        return redirect(url_for("main.assignments"))
    
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Verify teacher owns this assignment's course or TA is assigned to this course
    if current_user.role == 'instructor':
        if assignment.course.teacher != current_user.id:
            flash("You can only view submissions for your own courses.", "danger")
            return redirect(url_for("main.assignments"))
    else:  # TA
        ta_course_ids = [ta_assignment.course_id for ta_assignment in current_user.ta_assignments]
        if assignment.course_id not in ta_course_ids:
            flash("You can only view submissions for courses you are assigned to.", "danger")
            return redirect(url_for("main.assignments"))
    
    # Parse due date for late detection (stored as string yyyy-mm-dd)
    due_dt = None
    try:
        due_dt = datetime.strptime(str(assignment.due_date), "%Y-%m-%d")
    except Exception:
        due_dt = None

    # Get all submissions for this assignment with student info
    submissions = Submission.query.filter_by(assignment_id=assignment_id).all()

    submissions_with_status = []
    for sub in submissions:
        is_late = False
        if due_dt and sub.submitted_at:
            is_late = sub.submitted_at > due_dt
        submissions_with_status.append({"submission": sub, "is_late": is_late})
    
    # Create a form instance for CSRF protection
    form = GradeSubmissionForm()
    
    return render_template("main/view_submissions.html", assignment=assignment, submissions=submissions_with_status, form=form)

@bp.route("/grade_submission/<int:submission_id>", methods=["GET", "POST"])
@login_required
def grade_submission(submission_id):
    """Grade a student's submission (instructors and TAs only)"""
    if current_user.role not in ["instructor", "ta"]:
        flash("Access denied: instructors and TAs only.", "danger")
        return redirect(url_for("main.assignments"))
    
    submission = Submission.query.get_or_404(submission_id)
    assignment = submission.assignment
    
    # Verify teacher owns this assignment's course or TA is assigned to this course
    if current_user.role == 'instructor':
        if assignment.course.teacher != current_user.id:
            flash("You can only grade submissions for your own courses.", "danger")
            return redirect(url_for("main.assignments"))
    else:  # TA
        ta_course_ids = [ta_assignment.course_id for ta_assignment in current_user.ta_assignments]
        if assignment.course_id not in ta_course_ids:
            flash("You can only grade submissions for courses you are assigned to.", "danger")
            return redirect(url_for("main.assignments"))
    
    if request.method == "POST":
        grade = request.form.get("grade")
        try:
            grade_value = float(grade)
            if 0 <= grade_value <= 100:
                submission.grade = grade_value
                db.session.commit()
                flash(f"Grade {grade_value} saved for {submission.student.username}!", "success")
            else:
                flash("Grade must be between 0 and 100.", "danger")
        except (ValueError, TypeError):
            flash("Invalid grade value.", "danger")
    
    return redirect(url_for("main.view_submissions", assignment_id=assignment.id))

# ============= MESSAGING & COMMUNICATION ROUTES =============

@bp.route("/messages")
@login_required
def messages():
    """View inbox - all received messages"""
    inbox = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).all()
    unread_count = Message.query.filter_by(recipient_id=current_user.id, read=False).count()
    return render_template("main/messages.html", messages=inbox, unread_count=unread_count)

@bp.route("/messages/sent")
@login_required
def sent_messages():
    """View sent messages"""
    sent = Message.query.filter_by(sender_id=current_user.id).order_by(Message.timestamp.desc()).all()
    return render_template("main/sent_messages.html", messages=sent)

@bp.route("/messages/compose", methods=["GET", "POST"])
@login_required
def compose_message():
    """Compose and send a one-on-one message"""
    form = ComposeMessageForm()
    
    # Populate recipient choices based on user role
    if current_user.role == 'student':
        # Students can message instructors and TAs from their enrolled courses
        enrolled_course_ids = [e.course_id for e in current_user.courses_enrolled]
        courses = Course.query.filter(Course.id.in_(enrolled_course_ids)).all()
        
        # Get instructors and TAs from these courses
        instructor_ids = [c.teacher for c in courses]
        recipients = User.query.filter(
            ((User.id.in_(instructor_ids)) | (User.role == 'ta')) &
            (User.id != current_user.id)
        ).all()
    elif current_user.role == 'instructor':
        # Instructors can message students from courses they teach, plus other staff
        taught_courses = Course.query.filter_by(teacher=current_user.id).all()
        student_ids = []
        for course in taught_courses:
            enrollments = Enrollment.query.filter_by(course_id=course.id).all()
            student_ids.extend([e.student_id for e in enrollments])
        
        # Also include other instructors and TAs
        recipients = User.query.filter(
            ((User.id.in_(student_ids)) | (User.role.in_(['instructor', 'ta']))) &
            (User.id != current_user.id)
        ).all()
    else:  # TA
        # TAs can message students and instructors from their assigned courses only
        ta_course_ids = [ta_assignment.course_id for ta_assignment in current_user.ta_assignments]
        ta_courses = Course.query.filter(Course.id.in_(ta_course_ids)).all()
        
        # Get students from assigned courses
        student_ids = []
        instructor_ids = []
        for course in ta_courses:
            enrollments = Enrollment.query.filter_by(course_id=course.id).all()
            student_ids.extend([e.student_id for e in enrollments])
            instructor_ids.append(course.teacher)
        
        # Include students and instructors from assigned courses, plus other TAs
        recipients = User.query.filter(
            ((User.id.in_(student_ids)) | (User.id.in_(instructor_ids)) | (User.role == 'ta')) &
            (User.id != current_user.id)
        ).all()
    
    form.recipient_id.choices = [(u.id, f"{u.username} ({u.role})") for u in recipients]
    
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=form.recipient_id.data,
            subject=form.subject.data,
            body=form.body.data
        )
        db.session.add(message)
        db.session.commit()
        flash("Message sent successfully!", "success")
        return redirect(url_for("main.messages"))
    
    return render_template("main/compose_message.html", form=form)

@bp.route("/messages/<int:message_id>")
@login_required
def view_message(message_id):
    """View a specific message"""
    message = Message.query.get_or_404(message_id)
    
    # Ensure user is sender or recipient
    if message.sender_id != current_user.id and message.recipient_id != current_user.id:
        flash("You don't have permission to view this message.", "danger")
        return redirect(url_for("main.messages"))
    
    # Mark as read if recipient is viewing
    if message.recipient_id == current_user.id and not message.read:
        message.read = True
        db.session.commit()
    
    return render_template("main/view_message.html", message=message)

@bp.route("/announcements")
@login_required
def announcements():
    """View all announcements for user's courses"""
    if current_user.role == 'student':
        # Get announcements from enrolled courses
        enrolled_course_ids = [e.course_id for e in current_user.courses_enrolled]
        announcements_list = Announcement.query.filter(
            Announcement.course_id.in_(enrolled_course_ids)
        ).order_by(Announcement.timestamp.desc()).all()
    elif current_user.role == 'instructor':
        # Get announcements from taught courses
        taught_course_ids = [c.id for c in current_user.courses_taught]
        announcements_list = Announcement.query.filter(
            Announcement.course_id.in_(taught_course_ids)
        ).order_by(Announcement.timestamp.desc()).all()
    else:  # TA
        # TAs see announcements from their assigned courses only
        ta_course_ids = [ta_assignment.course_id for ta_assignment in current_user.ta_assignments]
        announcements_list = Announcement.query.filter(
            Announcement.course_id.in_(ta_course_ids)
        ).order_by(Announcement.timestamp.desc()).all()
    
    return render_template("main/announcements.html", announcements=announcements_list)

@bp.route("/announcements/create", methods=["GET", "POST"])
@login_required
def create_announcement():
    """Create a course-wide announcement (instructors and TAs only)"""
    if current_user.role not in ['instructor', 'ta']:
        flash("Only instructors and TAs can post announcements.", "danger")
        return redirect(url_for("main.announcements"))
    
    form = AnnouncementForm()
    
    # Populate course choices
    if current_user.role == 'instructor':
        courses = Course.query.filter_by(teacher=current_user.id).all()
    else:  # TA - only assigned courses
        ta_course_ids = [ta_assignment.course_id for ta_assignment in current_user.ta_assignments]
        courses = Course.query.filter(Course.id.in_(ta_course_ids)).all()
    
    form.course_id.choices = [(c.id, f"{c.title} ({c.code})") for c in courses]
    
    if not form.course_id.choices:
        flash("You don't have any courses to post announcements to.", "info")
        return redirect(url_for("main.announcements"))
    
    if form.validate_on_submit():
        announcement = Announcement(
            course_id=form.course_id.data,
            author_id=current_user.id,
            title=form.title.data,
            content=form.content.data
        )
        db.session.add(announcement)
        db.session.commit()
        flash("Announcement posted successfully!", "success")
        return redirect(url_for("main.announcements"))
    
    return render_template("main/create_announcement.html", form=form)

@bp.route("/<int:course_id>/grades")
@login_required
def view_course_grades(course_id):
    course = Course.query.get_or_404(course_id)

    # Get assignments for the course
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    
    # If student, get their submissions and grades
    submissions_dict = {}
    graded_count = 0
    avg_grade = None

    if current_user.role == 'student':
        submissions = Submission.query.filter_by(student_id=current_user.id).all()
        submissions_dict = {sub.assignment_id: sub for sub in submissions}

        graded_subs = [sub for sub in submissions if sub.grade is not None]
        graded_count = len(graded_subs)
        if graded_subs:
            avg_grade = round(sum(sub.grade for sub in graded_subs) / graded_count, 2)

    return render_template(
        "main/view_grades.html",
        course=course,
        assignments=assignments,
        submissions_dict=submissions_dict,
        graded_count=graded_count,
        avg_grade=avg_grade,
    )

