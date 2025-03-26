from django.db import models
from django.utils import timezone

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
    
    class Meta:
        app_label = 'course_management'

class CourseTime(models.Model):
    begin_time = models.DateTimeField(verbose_name='开始时间', blank=True, null=True)
    end_time = models.DateTimeField(verbose_name='结束时间', blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_times')
    teacher = models.ForeignKey('user_management.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='course_times')
    
    class Meta:
        app_label = 'course_management'
        verbose_name = '课程时间'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        course_title = self.course.title if self.course else "未知课程"
        begin = self.begin_time.strftime('%Y-%m-%d %H:%M') if self.begin_time else "未设置"
        end = self.end_time.strftime('%Y-%m-%d %H:%M') if self.end_time else "未设置"
        return f"{course_title}: {begin} - {end}"

class StudentCourse(models.Model):
    student = models.ForeignKey('user_management.Student', on_delete=models.SET_NULL, null=True, blank=True, related_name='student_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_courses')
    
    class Meta:
        app_label = 'course_management'

class ClassCourse(models.Model):
    class_id = models.ForeignKey('class_management.Class', on_delete=models.CASCADE, related_name='class_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='class_courses')
    
    class Meta:
        app_label = 'course_management'
