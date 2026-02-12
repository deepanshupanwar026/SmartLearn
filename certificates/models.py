from django.db import models
from django.conf import settings
from courses.models import Course


class Certificate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='certificates'
    )

    certificate_file = models.FileField(
        upload_to='certificates/',
        blank=True,
        null=True
    )

    issue_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
