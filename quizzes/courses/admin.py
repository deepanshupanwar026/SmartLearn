from django.contrib import admin
from .models import Course, Lesson, Category


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'instructor',
        'category',
        'status',
        'is_approved',
        'created_at',
    )
    list_filter = ('status', 'is_approved', 'category')
    search_fields = ('title', 'description')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    ordering = ('course', 'order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
