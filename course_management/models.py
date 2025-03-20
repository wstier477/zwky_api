from django.db import models

# Create your models here.

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=45)
    description = models.CharField(max_length=45, blank=True, null=True)
    location = models.CharField(max_length=45, blank=True, null=True)
    system = models.CharField(max_length=45, blank=True, null=True)
    schedule = models.CharField(max_length=45, blank=True, null=True)
    semester = models.CharField(max_length=45, blank=True, null=True)
    teacher = models.ForeignKey('user_management.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')

class CourseTime(models.Model):
    begin_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_times')
    teacher = models.ForeignKey('user_management.Teacher', on_delete=models.CASCADE, related_name='course_times')

class StudentCourse(models.Model):
    student = models.ForeignKey('user_management.Student', on_delete=models.CASCADE, related_name='student_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_courses')

class ClassCourse(models.Model):
    class_id = models.ForeignKey('class_management.Class', on_delete=models.CASCADE, related_name='class_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='class_courses')
