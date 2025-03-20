from django.contrib import admin
from .models import Course, CourseTime, StudentCourse, ClassCourse

admin.site.register(Course)
admin.site.register(CourseTime)
admin.site.register(StudentCourse)
admin.site.register(ClassCourse)
