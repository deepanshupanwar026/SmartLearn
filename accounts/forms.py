from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import User
import re


# ==================================================
# REGISTER FORM
# ==================================================
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mobile = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'mobile', 'password1', 'password2')

    # ---------------------------
    # USERNAME VALIDATION
    # ---------------------------
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) < 4:
            raise ValidationError("Username must be at least 4 characters long.")

        if username[0].isdigit():
            raise ValidationError("Username cannot start with a number.")

        if username.isdigit():
            raise ValidationError("Username cannot contain only numbers.")

        if not re.search(r'[A-Za-z]', username):
            raise ValidationError("Username must contain at least one letter.")

        if not re.match(r'^[A-Za-z0-9_]+$', username):
            raise ValidationError("Only letters, numbers and underscore (_) allowed.")

        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already taken.")

        return username.lower()

    # ---------------------------
    # EMAIL VALIDATION
    # ---------------------------
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered.")

        return email.lower()

    # ---------------------------
    # MOBILE VALIDATION (INDIA)
    # ---------------------------
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')

        mobile = mobile.strip()

        if not re.match(r'^[6-9]\d{9}$', mobile):
            raise ValidationError("Enter a valid 10-digit Indian mobile number.")

        return mobile

    # ---------------------------
    # PASSWORD MATCH
    # ---------------------------
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        return cleaned_data

    # ---------------------------
    # SAVE USER
    # ---------------------------
    def save(self, commit=True):
        user = super().save(commit=False)

        user.email = self.cleaned_data['email']
        user.mobile = self.cleaned_data['mobile']

        # Default values
        user.role = None
        user.has_chosen_role = False
        user.is_approved = False

        if commit:
            user.save()

        return user


# ==================================================
# LOGIN FORM
# ==================================================
class CustomAuthenticationForm(AuthenticationForm):
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not User.objects.filter(username=username).exists():
            raise ValidationError("No account found with this username.")

        return username


# ==================================================
# PROFILE UPDATE FORM
# ==================================================
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile', 'profile_picture']

    # ---------------------------
    # FIRST NAME VALIDATION
    # ---------------------------
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')

        if first_name:
            if first_name[0].isdigit():
                raise ValidationError("First name cannot start with a number.")

            if not re.match(r'^[A-Za-z ]+$', first_name):
                raise ValidationError("First name must contain only letters.")

        return first_name

    # ---------------------------
    # LAST NAME VALIDATION
    # ---------------------------
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if last_name:
            if last_name[0].isdigit():
                raise ValidationError("Last name cannot start with a number.")

            if not re.match(r'^[A-Za-z ]+$', last_name):
                raise ValidationError("Last name must contain only letters.")

        return last_name

    # ---------------------------
    # EMAIL UNIQUE CHECK
    # ---------------------------
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError("This email is already in use.")

        return email.lower()

    # ---------------------------
    # MOBILE VALIDATION
    # ---------------------------
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')

        if mobile:
            if not re.match(r'^[6-9]\d{9}$', mobile):
                raise ValidationError("Enter a valid 10-digit Indian mobile number.")

        return mobile
