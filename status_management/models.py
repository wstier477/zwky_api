from django.db import models

# Create your models here.

class Status(models.Model):
    concentrate = models.IntegerField()
    sleepy = models.IntegerField()
    low_head = models.IntegerField()
    half = models.IntegerField()
    puzzle = models.IntegerField()
    if_come = models.BooleanField(default=False)
    student = models.ForeignKey('user_management.Student', on_delete=models.CASCADE, related_name='statuses')
    course_time = models.ForeignKey('course_management.CourseTime', on_delete=models.CASCADE, related_name='statuses')
