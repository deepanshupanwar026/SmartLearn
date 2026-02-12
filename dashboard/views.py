from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Count
from quizzes.models import Quiz, QuizResult
from courses.models import Course, Lesson
from enrollments.models import Enrollment
from accounts.models import User
from certificates.models import Certificate
from accounts.forms import ProfileUpdateForm


# ----------------------------
# ROLE CHECKERS
# ----------------------------

def admin_required(user):
    return user.is_authenticated and user.role == 'admin'


def instructor_required(user):
    return user.is_authenticated and user.role == 'instructor'


def student_required(user):
    return user.is_authenticated and user.role == 'student'


# ----------------------------
# MAIN DASHBOARD REDIRECT
# ----------------------------

@login_required(login_url='/accounts/login/')
def main_dashboard(request):
    if request.user.role == 'student':
        return redirect('student_dashboard')
    elif request.user.role == 'instructor':
        return redirect('instructor_dashboard')
    elif request.user.role == 'admin':
        return redirect('admin_dashboard')
    else:
        raise PermissionDenied("Invalid role.")


# ----------------------------
# STUDENT DASHBOARD
# ----------------------------

@login_required(login_url='/accounts/login/')
def student_dashboard(request):
    if request.user.role != 'student':
        raise PermissionDenied("Students only.")

    enrollments = Enrollment.objects.filter(student=request.user)

    completed_courses = 0
    for e in enrollments:
        if e.progress_percent() == 100:
            completed_courses += 1

    certificates_count = Certificate.objects.filter(
        user=request.user
    ).count()

    return render(request, 'dashboard/student.html', {
        'enrollments': enrollments,
        'completed_courses': completed_courses,
        'certificates_count': certificates_count
    })


# ----------------------------
# STUDENT: PROFILE
# ----------------------------

@login_required(login_url='/accounts/login/')
def student_profile(request):
    if request.user.role != 'student':
        raise PermissionDenied("Students only.")

    return render(request, 'dashboard/student_profile.html')


@login_required(login_url='/accounts/login/')
def edit_profile(request):
    if request.user.role != 'student':
        raise PermissionDenied("Students only.")

    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('student_profile')

    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'dashboard/edit_profile.html', {
        'form': form
    })


# ----------------------------
# STUDENT: COURSES
# ----------------------------

@login_required(login_url='/accounts/login/')
def student_courses(request):
    if request.user.role != 'student':
        raise PermissionDenied("Students only.")

    enrollments = Enrollment.objects.filter(student=request.user)

    return render(request, 'dashboard/student_courses.html', {
        'enrollments': enrollments
    })


# ----------------------------
# STUDENT: NOTES
# ----------------------------

@login_required(login_url='/accounts/login/')
def student_notes(request):
    if request.user.role != 'student':
        raise PermissionDenied("Students only.")

    enrollments = Enrollment.objects.filter(student=request.user)
    courses = [e.course for e in enrollments]

    lessons = Lesson.objects.filter(
        course__in=courses,
        pdf_notes__isnull=False
    ).exclude(pdf_notes='')

    return render(request, 'dashboard/student_notes.html', {
        'lessons': lessons
    })


# ----------------------------
# STUDENT: CERTIFICATES
# ----------------------------

@login_required(login_url='/accounts/login/')
def student_certificates(request):
    if request.user.role != 'student':
        raise PermissionDenied("Students only.")

    certificates = Certificate.objects.filter(
        user=request.user,
        certificate_file__isnull=False
    )

    return render(request, 'dashboard/student_certificates.html', {
        'certificates': certificates
    })


# ----------------------------
# STUDENT: QUIZZES / ASSIGNMENTS
# ----------------------------

@login_required(login_url='/accounts/login/')
def student_quizzes(request):
    if request.user.role != 'student':
        raise PermissionDenied("Students only.")

    # Courses student is enrolled in
    enrollments = Enrollment.objects.filter(student=request.user)

    available_quizzes = []
    completed_quizzes = []

    for enrollment in enrollments:
        course = enrollment.course

        # Check if course has a quiz
        if hasattr(course, 'quiz'):
            quiz = course.quiz

            result = QuizResult.objects.filter(
                quiz=quiz,
                user=request.user
            ).first()

            if result:
                completed_quizzes.append({
                    'quiz': quiz,
                    'score': result.score,
                    'passed': result.passed
                })
            else:
                available_quizzes.append(quiz)

    return render(request, 'dashboard/student_quizzes.html', {
        'available_quizzes': available_quizzes,
        'completed_quizzes': completed_quizzes
    })


@login_required(login_url='/accounts/login/')
def student_assignments(request):
    if request.user.role != 'student':
        raise PermissionDenied("Students only.")

    return render(request, 'dashboard/student_assignments.html')


# ----------------------------
# INSTRUCTOR DASHBOARD
# ----------------------------

@login_required(login_url='/accounts/login/')
def instructor_dashboard(request):
    if request.user.role != 'instructor':
        raise PermissionDenied("Instructors only.")

    courses = Course.objects.filter(instructor=request.user)

    return render(request, 'dashboard/instructor.html', {
        'courses': courses
    })


# ----------------------------
# INSTRUCTOR: MY COURSES
# ----------------------------

@login_required(login_url='/accounts/login/')
def instructor_my_courses(request):
    if request.user.role != 'instructor':
        raise PermissionDenied("Instructors only.")

    courses = Course.objects.filter(instructor=request.user)

    return render(request, 'dashboard/instructor_my_courses.html', {
        'courses': courses
    })


# ----------------------------
# INSTRUCTOR: STUDENTS (DROPDOWN + COUNTS)
# ----------------------------

@login_required
def instructor_students(request):
    if request.user.role != 'instructor':
        raise PermissionDenied("Instructors only.")

    courses = Course.objects.filter(instructor=request.user)

    selected_course_id = request.GET.get('course')

    enrollments = Enrollment.objects.filter(
        course__instructor=request.user
    ).select_related('student', 'course')

    if selected_course_id:
        enrollments = enrollments.filter(course_id=selected_course_id)

    return render(request, 'dashboard/instructor_students.html', {
        'enrollments': enrollments,
        'courses': courses,
        'selected_course_id': selected_course_id,
    })



# ----------------------------
# INSTRUCTOR: ADD LESSONS
# ----------------------------

@login_required(login_url='/accounts/login/')
def instructor_add_lessons(request, course_id):
    if request.user.role != 'instructor':
        raise PermissionDenied("Instructors only.")

    course = get_object_or_404(
        Course,
        id=course_id,
        instructor=request.user
    )

    lessons = Lesson.objects.filter(course=course).order_by('order')

    if request.method == 'POST':
        Lesson.objects.create(
            course=course,
            title=request.POST.get('title'),
            youtube_url=request.POST.get('youtube_url'),
            pdf_notes=request.FILES.get('pdf_notes'),
            order=request.POST.get('order')
        )

        messages.success(request, "Lesson added successfully.")
        return redirect('instructor_add_lessons', course_id=course.id)

    return render(request, 'courses/instructor_add_lessons.html', {
        'course': course,
        'lessons': lessons
    })


# ----------------------------
# INSTRUCTOR: PROFILE
# ----------------------------

@login_required(login_url='/accounts/login/')
def instructor_profile(request):
    if request.user.role != 'instructor':
        raise PermissionDenied("Instructors only.")

    return render(request, 'dashboard/instructor_profile.html')


@login_required(login_url='/accounts/login/')
def instructor_edit_profile(request):
    if request.user.role != 'instructor':
        raise PermissionDenied("Instructors only.")

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        parts = full_name.split(' ')
        request.user.first_name = parts[0] if parts else ''
        request.user.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

        request.user.email = request.POST.get('email')
        request.user.mobile = request.POST.get('mobile')

        if 'profile_picture' in request.FILES:
            request.user.profile_picture = request.FILES.get('profile_picture')

        request.user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('instructor_profile')

    return render(request, 'dashboard/instructor_edit_profile.html')


# ----------------------------
# INSTRUCTOR: QUIZZES (PLACEHOLDER)
# ----------------------------

@login_required(login_url='/accounts/login/')
def instructor_quizzes(request):
    if request.user.role != 'instructor':
        raise PermissionDenied("Instructors only.")

    return render(request, 'dashboard/instructor_quizzes.html')


# ----------------------------
# INSTRUCTOR: ANALYTICS (PLACEHOLDER)
# ----------------------------

@login_required(login_url='/accounts/login/')
def instructor_analytics(request):
    if request.user.role != 'instructor':
        raise PermissionDenied("Instructors only.")

    return render(request, 'dashboard/instructor_analytics.html')


# ----------------------------
# ADMIN DASHBOARD
# ----------------------------

@login_required(login_url='/accounts/login/')
def admin_dashboard(request):
    if request.user.role != 'admin':
        raise PermissionDenied("Admins only.")

    users_count = User.objects.count()
    courses_count = Course.objects.count()
    enrollments_count = Enrollment.objects.count()

    return render(request, 'dashboard/admin.html', {
        'users': users_count,
        'courses': courses_count,
        'enrollments': enrollments_count
    })


# ----------------------------
# ADMIN: APPROVE INSTRUCTORS
# ----------------------------

@user_passes_test(admin_required, login_url='/accounts/login/')
def approve_instructors(request):
    pending = User.objects.filter(
        role='instructor',
        is_approved=False
    )

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.is_approved = True
        user.save()

        return redirect('approve_instructors')

    return render(request, 'dashboard/approve_instructors.html', {
        'pending': pending
    })


# ----------------------------
# ADMIN: APPROVE COURSES
# ----------------------------

@user_passes_test(admin_required, login_url='/accounts/login/')
def approve_courses(request):
    pending = Course.objects.filter(is_approved=False)

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        course.is_approved = True
        course.status = 'published'
        course.save()

        return redirect('approve_courses')

    return render(request, 'dashboard/approve_courses.html', {
        'pending': pending
    })
