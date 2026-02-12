from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username

    # 🔥 REQUIRED TO AVOID AUTH CLASH
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='accounts_user_set',
        related_query_name='accounts_user',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='accounts_user_set',
        related_query_name='accounts_user',
    )
