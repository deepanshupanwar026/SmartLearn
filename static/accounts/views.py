from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User

from django.contrib import messages
from django.contrib.auth import authenticate , login, logout



# ----------------------------
# ROLE SELECTION BEFORE REGISTER
# ----------------------------

def choose_role(request):
    if request.method == "POST":
        role = request.POST.get("role")

        if role == "student":
            return redirect("register_student")

        elif role == "instructor":
            return redirect("register_instructor")

    return render(request, "accounts/choose_role.html")


# ----------------------------
# REGISTER
# ----------------------------

def register(request):
    selected_role = request.session.get('selected_role')

    # Force role selection before register
    if not selected_role:
        return redirect('choose_role')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = selected_role

            # Student auto-approved
            if selected_role == 'student':
                user.is_approved = True

            # Instructor needs admin approval
            if selected_role == 'instructor':
                user.is_approved = False

            user.save()

            del request.session['selected_role']

            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    messages.success(request, " You can now register now .")

    return render(request, 'accounts/register.html', {
        'form': form,
        'selected_role': selected_role
    })


# ----------------------------
# LOGIN
# ----------------------------

def user_login(request):
    form = CustomAuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)

        # 🔥 ROLE BASED REDIRECT
        if user.role == 'instructor':
            return redirect('instructor_dashboard')
        elif user.role == 'student':
            return redirect('student_dashboard')
        elif user.role == 'admin':
            return redirect('admin_dashboard')
        
        messages.success(request, "You have successfully logged in.")

        return redirect('home')

    return render(request, 'accounts/login.html', {'form': form})


# ----------------------------
# LOGOUT
# ----------------------------

def user_logout(request):
    logout(request)
    from django.contrib import messages
    messages.info(request, "You have logged out successfully.")
    return redirect('home')



def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # 🔍 Check if user exists
        if not User.objects.filter(username=username).exists():
            messages.error(request, "This account is not registered.")
            return redirect("login")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid password.")
            return redirect("login")

        # 🔒 Instructor approval check
        if user.role == "instructor" and not user.is_approved:
            messages.warning(
                request,
                "Your instructor account is not approved yet. Please wait for admin approval."
            )
            return redirect("login")

        login(request, user)
        return redirect("main_dashboard")

    return render(request, "accounts/login.html")


def custom_logout(request):
    logout(request)
    return redirect("login")


def register_student(request):
    request.session["selected_role"] = "student"

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = "student"
            user.is_approved = True
            user.save()

            messages.success(request, "Account created successfully. You can now log in.")
            return redirect("login")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {
        "form": form,
        "selected_role": "student"
    })

def register_instructor(request):
    request.session["selected_role"] = "instructor"

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = "instructor"
            user.is_approved = False
            user.save()

            messages.info(
                request,
                "Your instructor account is created. Please wait for admin approval."
            )
            return redirect("login")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {
        "form": form,
        "selected_role": "instructor"
    })
