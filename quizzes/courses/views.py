from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib import messages
from .models import Course, Lesson, Category
from enrollments.models import Enrollment, LessonProgress
from quizzes.models import Quiz, QuizResult
from certificates.models import Certificate

# ----------------------------
# HOME + SEARCH
# ----------------------------

def home(request):
    query = request.GET.get('q', '')

    courses = Course.objects.filter(status='published')

    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    return render(request, 'courses/home.html', {
        'courses': courses,
        'query': query
    })


# ----------------------------
# COURSES LIST PAGE
# ----------------------------

def courses_list(request):
    query = request.GET.get('q', '')

    courses = Course.objects.filter(status='published')

    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    return render(request, 'courses/courses_list.html', {
        'courses': courses,
        'query': query
    })


# ----------------------------
# COURSE DETAIL
# ----------------------------

@login_required(login_url='/accounts/login/')
def course_detail(request, pk):
    course = get_object_or_404(Course, id=pk)

    enrolled = False
    completed_all = False
    has_quiz = hasattr(course, "quiz")
    quiz_passed = False

    enrollment = Enrollment.objects.filter(
        course=course,
        student=request.user
    ).first()

    if enrollment:
        enrolled = True

        total_lessons = course.lesson_set.count()
        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).count()

        completed_all = total_lessons > 0 and completed_lessons == total_lessons

        if has_quiz:
            quiz_passed = QuizResult.objects.filter(
                quiz=course.quiz,
                user=request.user,
                passed=True
            ).exists()

    lessons = course.lesson_set.all()

    return render(request, "courses/course_detail.html", {
        "course": course,
        "lessons": lessons,
        "enrolled": enrolled,
        "completed_all": completed_all,
        "has_quiz": has_quiz,
        "quiz_passed": quiz_passed,
    })




# ----------------------------
# LESSON PLAYER + PROGRESS
# ----------------------------

@login_required(login_url='/accounts/login/')
def lesson_player(request, course_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course_id=course_id)
    course = lesson.course

    enrollment = get_object_or_404(
        Enrollment,
        student=request.user,
        course=course
    )

    # Current lesson progress
    lesson_progress, _ = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    # 🔒 CHECK PREVIOUS LESSON
    previous_lesson = (
        Lesson.objects
        .filter(course=course, order__lt=lesson.order)
        .order_by('-order')
        .first()
    )

    if previous_lesson:
        prev_completed = LessonProgress.objects.filter(
            enrollment=enrollment,
            lesson=previous_lesson,
            completed=True
        ).exists()

        if not prev_completed:
            from django.contrib import messages
            messages.warning(
                request,
                "Please complete the previous lesson first 🔒"
            )
            return redirect(
                'lesson_player',
                course.id,
                previous_lesson.id
            )

    # COURSE PROGRESS
    total_lessons = course.lesson_set.count()
    completed_lessons = LessonProgress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).count()

    progress_percent = int((completed_lessons / total_lessons) * 100) if total_lessons else 0
    course_completed = progress_percent == 100

    # LESSON SIDEBAR DATA
    lessons = course.lesson_set.order_by('order')
    lesson_map = []

    for l in lessons:
        completed = LessonProgress.objects.filter(
            enrollment=enrollment,
            lesson=l,
            completed=True
        ).exists()

        locked = False
        if l.order > 1:
            prev = Lesson.objects.filter(
                course=course,
                order=l.order - 1
            ).first()

            if prev:
                locked = not LessonProgress.objects.filter(
                    enrollment=enrollment,
                    lesson=prev,
                    completed=True
                ).exists()

        l.completed = completed
        l.locked = locked
        lesson_map.append(l)

    quiz = getattr(course, "quiz", None)

    return render(request, "courses/lesson_player.html", {
        "lesson": lesson,
        "course": course,
        "lessons": lesson_map,
        "lesson_progress": lesson_progress,
        "progress_percent": progress_percent,
        "course_completed": course_completed,
        "quiz": quiz,
    })



# ----------------------------
# RESUME COURSE
# ----------------------------

@login_required(login_url='/accounts/login/')
def resume_course(request, course_id):
    enrollment = get_object_or_404(
        Enrollment,
        student=request.user,
        course_id=course_id
    )

    last = LessonProgress.objects.filter(
        enrollment=enrollment,
        completed=False
    ).order_by('lesson__order').first()

    if last:
        return redirect(
            'lesson_player',
            course_id=course_id,
            lesson_id=last.lesson.id
        )

    first = Lesson.objects.filter(
        course_id=course_id
    ).order_by('order').first()

    return redirect(
        'lesson_player',
        course_id=course_id,
        lesson_id=first.id
    )


# ----------------------------
# INSTRUCTOR PERMISSION
# ----------------------------

def instructor_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/')
        if request.user.role != 'instructor' or not request.user.is_approved:
            raise PermissionDenied("Instructor approval required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ----------------------------
# CREATE COURSE
# ----------------------------

@instructor_required
def create_course(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')

        category = get_object_or_404(Category, id=category_id)

        Course.objects.create(
            instructor=request.user,
            title=title,
            description=description,
            category=category,
            status='draft',
            is_approved=False
        )

        messages.success(request, "Course created successfully. Waiting for admin approval.")
        return redirect('instructor_dashboard')

    categories = Category.objects.all()

    return render(request, 'courses/create_course.html', {
        'categories': categories
    })


# ----------------------------
# ENROLL COURSE
# ----------------------------

@login_required(login_url='/accounts/login/')
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # 🔒 Only students can enroll
    if request.user.role != 'student':
        raise PermissionDenied("Only students can enroll in courses.")

    Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )
    messages.success(request, "You have successfully enrolled in this course.")
    return redirect('course_detail', pk=course.id)



# ----------------------------
# INSTRUCTOR: ADD LESSONS
# ----------------------------

@login_required
def instructor_add_lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.instructor:
        raise PermissionDenied("Not allowed.")

    if not course.is_approved:
        raise PermissionDenied("Course not approved yet.")

    lessons = Lesson.objects.filter(course=course).order_by('order')

    if request.method == 'POST':
        Lesson.objects.create(
        course=course,
        title=request.POST.get('title'),
        youtube_url=request.POST.get('youtube_url') or None,
        video_file=request.FILES.get('video_file'),
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
# INSTRUCTOR: EDIT LESSON
# ----------------------------


@login_required
def instructor_edit_lesson(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    if request.user != course.instructor:
        raise PermissionDenied("Not allowed.")

    if not course.is_approved:
        raise PermissionDenied("Course not approved.")

    if request.method == 'POST':
        lesson.title = request.POST.get('title')
        lesson.youtube_url = request.POST.get('youtube_url') or None
        lesson.order = request.POST.get('order')

        if request.FILES.get('video_file'):
            lesson.video_file = request.FILES.get('video_file')

        if request.FILES.get('pdf_notes'):
            lesson.pdf_notes = request.FILES.get('pdf_notes')

        lesson.save()

        messages.success(request, "Lesson updated successfully.")
        return redirect('instructor_add_lessons', course_id=course.id)

    return render(request, 'courses/instructor_edit_lesson.html', {
        'lesson': lesson,
        'course': course
    })




# ----------------------------
# INSTRUCTOR: DELETE LESSON
# ----------------------------

from django.contrib import messages

@login_required
def instructor_delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    if request.user != course.instructor:
        raise PermissionDenied("Not allowed.")

    if not course.is_approved:
        raise PermissionDenied("Course not approved.")

    lesson.delete()

    messages.success(request, "Lesson deleted successfully.")
    return redirect('instructor_add_lessons', course_id=course.id)



# ----------------------------
# INSTRUCTOR: MY COURSES
# ----------------------------

@login_required
def instructor_my_courses(request):
    if request.user.role != 'instructor':
        raise PermissionDenied("Instructors only.")

    courses = Course.objects.filter(instructor=request.user)

    return render(request, 'dashboard/instructor_my_courses.html', {
        'courses': courses
    })


# ----------------------------
# INSTRUCTOR: STUDENTS
# ----------------------------

@login_required
def instructor_students(request):
    if request.user.role != 'instructor':
        raise PermissionDenied("Instructors only.")

    enrollments = Enrollment.objects.filter(
        course__instructor=request.user
    ).select_related('student', 'course')

    return render(request, 'dashboard/instructor_students.html', {
        'enrollments': enrollments
    })


# ----------------------------
# INSTRUCTOR: QUIZZES (STUB)
# ----------------------------

@login_required
def instructor_quizzes(request):
    if request.user.role != 'instructor':
        raise PermissionDenied("Instructors only.")

    return render(request, 'dashboard/instructor_quizzes.html')


@login_required(login_url='/accounts/login/')
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    enrollment = Enrollment.objects.get(
        student=request.user,
        course=course
    )

    lesson_progress, _ = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    total_lessons = course.lesson_set.count()
    completed_lessons = LessonProgress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).count()

    progress_percent = int((completed_lessons / total_lessons) * 100) if total_lessons else 0
    course_completed = progress_percent == 100

    lessons = course.lesson_set.all()
    lesson_map = []

    for l in lessons:
        lp = LessonProgress.objects.filter(
            enrollment=enrollment,
            lesson=l,
            completed=True
        ).exists()

        l.completed = lp
        lesson_map.append(l)

    quiz = getattr(course, "quiz", None)

    return render(request, "courses/lesson_detail.html", {
        "lesson": lesson,
        "course": course,
        "lessons": lesson_map,
        "lesson_progress": lesson_progress,
        "progress_percent": progress_percent,
        "course_completed": course_completed,
        "quiz": quiz,
    })

@login_required
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    enrollment = get_object_or_404(
        Enrollment,
        student=request.user,
        course=lesson.course
    )

    progress = get_object_or_404(
        LessonProgress,
        enrollment=enrollment,
        lesson=lesson
    )

    progress.completed = True
    progress.save()

    return redirect("lesson_player", lesson.course.id, lesson.id)


def home(request):
    courses = Course.objects.filter(status='published')[:8]

    return render(request, 'courses/home.html', {
        'courses': courses
    })

