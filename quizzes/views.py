from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from courses.models import Course
from enrollments.models import Enrollment, LessonProgress
from certificates.models import Certificate
from certificates.utils import generate_certificate_pdf

from .models import Quiz, Question, QuizResult


# =====================================================
# STUDENT: TAKE QUIZ
# =====================================================

@login_required(login_url='/accounts/login/')
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course

    # Only enrolled students
    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).first()

    if not enrollment:
        raise PermissionDenied("You must enroll to take this quiz.")

    # Must complete all lessons
    total_lessons = course.lesson_set.count()
    completed_lessons = LessonProgress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).count()

    if total_lessons > 0 and completed_lessons < total_lessons:
        raise PermissionDenied("Complete all lessons before attempting the quiz.")

    questions = quiz.questions.all()

    # ======================
    # QUIZ SUBMISSION
    # ======================
    if request.method == 'POST':
        correct = 0
        total = questions.count()

        for q in questions:
            selected = request.POST.get(str(q.id))
            if selected and int(selected) == q.correct_option:
                correct += 1

        percent = int((correct / total) * 100) if total > 0 else 0
        passed = percent >= quiz.pass_mark

        quiz_result, created = QuizResult.objects.get_or_create(
    quiz=quiz,
    user=request.user,
    defaults={
        'score': percent,
        'passed': passed
    }
)


        certificate = None

        # 🎓 CERTIFICATE GENERATION
        if passed:
            cert, created = Certificate.objects.get_or_create(
                user=request.user,
                course=course
            )

            if not cert.certificate_file:
                pdf_file = generate_certificate_pdf(
                    user=request.user,
                    course=course
                )

                if pdf_file:
                    cert.certificate_file.save(pdf_file.name, pdf_file)
                    cert.save()


        return render(request, 'quizzes/result.html', {
            'quiz': quiz,
            'correct': correct,
            'total': total,
            'percent': percent,
            'passed': passed,
            'pass_mark': quiz.pass_mark,
            'certificate': certificate
        })

    # ======================
    # QUIZ PAGE (GET)
    # ======================
    return render(request, 'quizzes/quiz_detail.html', {
        'quiz': quiz,
        'questions': questions
    })



# =====================================================
# INSTRUCTOR: QUIZ LIST
# =====================================================

@login_required(login_url='/accounts/login/')
def instructor_quizzes(request):
    if request.user.role != 'instructor':
        raise PermissionDenied("Instructors only.")

    quizzes = Quiz.objects.filter(course__instructor=request.user)

    return render(request, 'quizzes/instructor_quizzes.html', {
        'quizzes': quizzes
    })


# =====================================================
# INSTRUCTOR: CREATE QUIZ
# =====================================================

@login_required(login_url='/accounts/login/')
def instructor_create_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.instructor:
        raise PermissionDenied("Not allowed.")

    # One quiz per course
    if hasattr(course, 'quiz'):
        messages.warning(request, "This course already has a quiz.")
        return redirect('instructor_quizzes')

    if request.method == 'POST':
        title = request.POST.get('title')
        pass_mark = request.POST.get('pass_mark')

        if not title or not pass_mark:
            messages.error(request, "All fields are required.")
            return redirect(
                'instructor_create_quiz',
                course_id=course.id
            )

        Quiz.objects.create(
            course=course,
            title=title,
            pass_mark=int(pass_mark),
            total_marks=100
        )

        messages.success(request, "Quiz created successfully.")
        return redirect('instructor_quizzes')

    return render(request, 'quizzes/instructor_create_quiz.html', {
        'course': course
    })


# =====================================================
# INSTRUCTOR: MANAGE QUESTIONS
# =====================================================

@login_required(login_url='/accounts/login/')
def instructor_manage_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course

    if request.user != course.instructor:
        raise PermissionDenied("Not allowed.")

    questions = quiz.questions.all()

    if request.method == 'POST':
        text = request.POST.get('text')
        option1 = request.POST.get('option1')
        option2 = request.POST.get('option2')
        option3 = request.POST.get('option3')
        option4 = request.POST.get('option4')
        correct_option = request.POST.get('correct_option')

        if not all([
            text, option1, option2, option3, option4, correct_option
        ]):
            messages.error(request, "All fields are required.")
            return redirect(
                'instructor_manage_questions',
                quiz_id=quiz.id
            )

        Question.objects.create(
            quiz=quiz,
            text=text,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=int(correct_option)
        )

        messages.success(request, "Question added successfully.")
        return redirect(
            'instructor_manage_questions',
            quiz_id=quiz.id
        )

    return render(request, 'quizzes/instructor_manage_questions.html', {
        'quiz': quiz,
        'questions': questions
    })


# =====================================================
# INSTRUCTOR: QUIZ RESULTS (PER STUDENT)
# =====================================================

@login_required(login_url='/accounts/login/')
def instructor_quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course

    if request.user != course.instructor:
        raise PermissionDenied("Not allowed.")

    results = QuizResult.objects.filter(
        quiz=quiz
    ).select_related('user')

    return render(request, 'quizzes/instructor_quiz_results.html', {
        'quiz': quiz,
        'results': results
    })
