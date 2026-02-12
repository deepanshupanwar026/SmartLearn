from django.contrib import admin
from .models import Quiz, Question, QuizResult


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'pass_mark', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'course__title')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'correct_option')
    list_filter = ('quiz',)
    search_fields = ('text',)


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'passed', 'attempted_at')
    list_filter = ('passed', 'quiz')
    search_fields = ('user__username', 'quiz__title')
