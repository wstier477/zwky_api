from django.contrib import admin
from .models import Course, CourseTime, StudentCourse, ClassCourse, CourseAnnouncement, Assignment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'title', 'location', 'semester', 'teacher')
    search_fields = ('title', 'location', 'semester')
    list_filter = ('semester', 'teacher')

@admin.register(CourseTime)
class CourseTimeAdmin(admin.ModelAdmin):
    list_display = ('course', 'begin_time', 'end_time', 'teacher')
    search_fields = ('course__title',)
    list_filter = ('course', 'teacher')

@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ('student', 'course')
    search_fields = ('student__user__username', 'course__title')
    list_filter = ('course',)

@admin.register(ClassCourse)
class ClassCourseAdmin(admin.ModelAdmin):
    list_display = ('class_id', 'course')
    search_fields = ('class_id__class_name', 'course__title')
    list_filter = ('course', 'class_id')

@admin.register(CourseAnnouncement)
class CourseAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'type', 'created_by', 'created_at')
    search_fields = ('title', 'content', 'course__title')
    list_filter = ('type', 'course', 'created_at')
    date_hierarchy = 'created_at'

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'type', 'start_time', 'deadline', 'full_score', 'created_by')
    search_fields = ('title', 'description', 'course__title')
    list_filter = ('type', 'course', 'start_time', 'deadline')
    date_hierarchy = 'start_time'
