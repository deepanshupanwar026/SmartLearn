from django.urls import path
from . import views

urlpatterns = [

    path('', views.main_dashboard, name='main_dashboard'),

    # STUDENT
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/profile/edit/', views.edit_profile, name='edit_profile'),
    path('student/notes/', views.student_notes, name='student_notes'),
    path('student/certificates/', views.student_certificates, name='student_certificates'),
    path('student/courses/', views.student_courses, name='student_courses'),
    path('student/quizzes/', views.student_quizzes, name='student_quizzes'),
    path('student/assignments/', views.student_assignments, name='student_assignments'),


    # INSTRUCTOR
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/profile/', views.instructor_profile, name='instructor_profile'),
    path('instructor/profile/edit/', views.instructor_edit_profile, name='instructor_edit_profile'),
    path('instructor/courses/', views.instructor_my_courses, name='instructor_my_courses'),
    path('instructor/students/', views.instructor_students, name='instructor_students'),
    path('instructor/quizzes/', views.instructor_quizzes, name='instructor_quizzes'),
    path('instructor/analytics/', views.instructor_analytics, name='instructor_analytics'),
    path('instructor/course/<int:course_id>/lessons/',views.instructor_add_lessons,name='instructor_add_lessons'),


    # ADMIN
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/approve-instructors/', views.approve_instructors, name='approve_instructors'),
    path('admin/approve-courses/', views.approve_courses, name='approve_courses'),

]
