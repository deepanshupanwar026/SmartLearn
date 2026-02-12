from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Course, Lesson
from .models import Enrollment, LessonProgress
from .models import Payment

@login_required(login_url='/accounts/login/')
def pay_for_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    payment = Payment.objects.create(
        user=request.user,
        course=course,
        amount=course.price,
        status='completed',
        transaction_id='TXN' + str(course.id) + str(request.user.id)
    )

    Enrollment.objects.get_or_create(
    student_id=request.user.id,
    course_id=course.id
)

    
    return redirect('course_detail', pk=course.id)


@login_required(login_url='/accounts/login/')
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )

    # auto-create progress rows
    lessons = Lesson.objects.filter(course=course)
    for lesson in lessons:
        LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )

    return redirect('course_detail', pk=course.id)
