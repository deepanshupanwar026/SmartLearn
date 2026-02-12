from django.urls import path
from . import views

urlpatterns = [
    path('pay/<int:course_id>/', views.pay_for_course, name='pay_for_course'),

    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
]
