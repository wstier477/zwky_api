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

class CourseResource(models.Model):
    """课程资源模型"""
    RESOURCE_TYPE_CHOICES = (
        ('document', '文档'),
        ('image', '图片'),
        ('video', '视频'),
        ('other', '其他'),
    )
    
    name = models.CharField(verbose_name='资源名称', max_length=100)
    type = models.CharField(verbose_name='资源类型', max_length=20, choices=RESOURCE_TYPE_CHOICES, default='document')
    size = models.CharField(verbose_name='文件大小', max_length=20, blank=True, null=True)
    file = models.FileField(verbose_name='资源文件', upload_to='course_resources/%Y/%m/')
    description = models.TextField(verbose_name='资源描述', blank=True, null=True)
    upload_time = models.DateTimeField(verbose_name='上传时间', default=timezone.now)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    download_count = models.IntegerField(verbose_name='下载次数', default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    uploader = models.ForeignKey('user_management.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_resources')
    
    class Meta:
        app_label = 'course_management'
        verbose_name = '课程资源'
        verbose_name_plural = verbose_name
        ordering = ['-upload_time']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
