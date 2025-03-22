from django.contrib import admin
from .models import Course, CourseTime, StudentCourse, ClassCourse

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'title', 'teacher', 'system', 'semester', 'location')
    list_filter = ('system', 'semester', 'teacher')
    search_fields = ('title', 'description', 'location')

@admin.register(CourseTime)
class CourseTimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'teacher', 'begin_time', 'end_time')
    list_filter = ('course', 'teacher')
    search_fields = ('course__title', 'teacher__user__username')

@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course')
    list_filter = ('student', 'course')
    search_fields = ('student__user__username', 'course__title')

@admin.register(ClassCourse)
class ClassCourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_id', 'course')
    list_filter = ('class_id', 'course')
    search_fields = ('class_id__class_name', 'course__title')
