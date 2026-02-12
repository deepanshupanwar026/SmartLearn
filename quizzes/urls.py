from django.urls import path
from . import views

urlpatterns = [
    # Instructor quiz dashboard
    path('instructor/', views.instructor_quizzes, name='instructor_quizzes'),

    # Create quiz for a course
    path('instructor/create/<int:course_id>/', views.instructor_create_quiz, name='instructor_create_quiz'),

    # Manage questions of a quiz
    path('instructor/<int:quiz_id>/questions/', views.instructor_manage_questions, name='instructor_manage_questions'),

    # View results of a quiz
    path('instructor/<int:quiz_id>/results/', views.instructor_quiz_results, name='instructor_quiz_results'),

    # Student quiz attempt
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
]
