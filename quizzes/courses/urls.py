from django.urls import path
from . import views

urlpatterns = [

    # ----------------------------
    # PUBLIC / STUDENT
    # ----------------------------

    path('', views.home, name='home'),
    path('courses/', views.courses_list, name='courses_list'),

    path('course/<int:pk>/', views.course_detail, name='course_detail'),

     
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),

    path('course/<int:course_id>/lesson/<int:lesson_id>/',views.lesson_player,name='lesson_player'),

    path('course/<int:course_id>/resume/',views.resume_course,name='resume_course'),

    # ----------------------------
    # INSTRUCTOR: COURSE CREATION
    # ----------------------------

    path('create/', views.create_course, name='create_course'),

    path('instructor/course/<int:course_id>/lessons/',views.instructor_add_lessons,name='instructor_add_lessons'),

    path('instructor/course/<int:course_id>/lesson/<int:lesson_id>/edit/',views.instructor_edit_lesson,name='instructor_edit_lesson'),

    path('instructor/course/<int:course_id>/lesson/<int:lesson_id>/delete/',views.instructor_delete_lesson,name='instructor_delete_lesson'),

    # ----------------------------
    # INSTRUCTOR: DASHBOARD SECTIONS
    # ----------------------------

    path(
        'instructor/my-courses/',
        views.instructor_my_courses,
        name='instructor_my_courses'
    ),

    path(
        'instructor/students/',
        views.instructor_students,
        name='instructor_students'
    ),

    path(
        'instructor/quizzes/',
        views.instructor_quizzes,
        name='instructor_quizzes'
    ),

path("lesson/<int:lesson_id>/complete/", views.mark_lesson_complete, name="mark_lesson_complete"),

]
