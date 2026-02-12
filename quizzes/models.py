from django.db import models
from courses.models import Course
from accounts.models import User


class Quiz(models.Model):
    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name='quiz'
    )
    title = models.CharField(max_length=200)
    pass_mark = models.IntegerField(default=50)  # % needed to pass
    total_marks = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()

    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)

    correct_option = models.IntegerField(
    choices=[
        (1, 'Option 1'),
        (2, 'Option 2'),
        (3, 'Option 3'),
        (4, 'Option 4'),
    ],
    default=1
)


    def __str__(self):
        return self.text[:50]


class QuizResult(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='results'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_results'
    )
    score = models.IntegerField()
    passed = models.BooleanField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('quiz', 'user')
        

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}%"
