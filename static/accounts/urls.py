from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.choose_role, name="choose_role"),
    path("register/student/", views.register_student, name="register_student"),
    path("register/instructor/", views.register_instructor, name="register_instructor"),

    path("login/", views.custom_login, name="login"),
    path("logout/", views.custom_logout, name="logout"),
]

