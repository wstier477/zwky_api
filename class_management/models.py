from django.db import models

# Create your models here.

class Class(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=45)
    class_system = models.CharField(max_length=45)

class TeacherClass(models.Model):
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='teacher_classes')
    teacher = models.ForeignKey('user_management.Teacher', on_delete=models.CASCADE, related_name='teacher_classes')
