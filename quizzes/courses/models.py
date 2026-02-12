from django.db import models
from accounts.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Course(models.Model):
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'instructor'}
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('published', 'Published')],
        default='draft'
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)

    youtube_url = models.URLField(blank=True, null=True)

    # ✅ NEW: direct video upload
    video_file = models.FileField(
        upload_to='lesson_videos/',
        blank=True,
        null=True
    )

    pdf_notes = models.FileField(
        upload_to='notes/',
        blank=True,
        null=True
    )

    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('course', 'order')
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.title}"

    @property
    def youtube_embed_url(self):
        if not self.youtube_url:
            return None

        import re
        patterns = [
            r'youtube\.com/watch\?v=([^&]+)',
            r'youtu\.be/([^?&]+)',
            r'youtube\.com/embed/([^?&]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, self.youtube_url)
            if match:
                video_id = match.group(1)
                return f"https://www.youtube.com/embed/{video_id}"

        return None
