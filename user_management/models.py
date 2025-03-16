from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """
    自定义用户模型
    """
    ROLE_CHOICES = (
        ('teacher', '教师'),
        ('student', '学生'),
    )
    
    email = models.EmailField(verbose_name='邮箱', unique=True)
    phone = models.CharField(verbose_name='电话号码', max_length=20, blank=True, null=True)
    role = models.CharField(verbose_name='角色', max_length=10, choices=ROLE_CHOICES, default='student')
    avatar = models.URLField(verbose_name='头像URL', blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', default=timezone.now)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
