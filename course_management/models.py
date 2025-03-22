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
        verbose_name = '课程'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return f"{self.title} (ID: {self.course_id})"

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
        verbose_name = '学生选课'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        student_name = self.student.username if self.student else "未知学生"
        course_title = self.course.title if self.course else "未知课程"
        return f"{student_name} - {course_title}"

class ClassCourse(models.Model):
    class_id = models.ForeignKey('class_management.Class', on_delete=models.CASCADE, related_name='class_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='class_courses')
    
    class Meta:
        app_label = 'course_management'
        verbose_name = '班级课程'
        verbose_name_plural = verbose_name
        
    def __str__(self):
        class_name = self.class_id.class_name if self.class_id else "未知班级"
        course_title = self.course.title if self.course else "未知课程"
        return f"{class_name} - {course_title}"

class CourseAnnouncement(models.Model):
    """课程公告模型"""
    TYPE_CHOICES = (
        ('info', '普通'),
        ('warning', '重要'),
        ('danger', '紧急'),
    )
    
    title = models.CharField(verbose_name='标题', max_length=100)
    content = models.TextField(verbose_name='内容')
    type = models.CharField(verbose_name='类型', max_length=10, choices=TYPE_CHOICES, default='info')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements')
    created_by = models.ForeignKey('user_management.User', on_delete=models.SET_NULL, null=True, related_name='created_announcements')
    created_at = models.DateTimeField(verbose_name='创建时间', default=timezone.now)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    
    class Meta:
        app_label = 'course_management'
        verbose_name = '课程公告'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.course.title} - {self.title} ({self.get_type_display()})"

class Assignment(models.Model):
    """作业/考试模型"""
    TYPE_CHOICES = (
        ('homework', '作业'),
        ('exam', '考试'),
    )
    
    title = models.CharField(verbose_name='标题', max_length=100)
    type = models.CharField(verbose_name='类型', max_length=10, choices=TYPE_CHOICES, default='homework')
    description = models.TextField(verbose_name='描述')
    start_time = models.DateTimeField(verbose_name='开始时间')
    deadline = models.DateTimeField(verbose_name='截止时间')
    full_score = models.IntegerField(verbose_name='总分', default=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    created_by = models.ForeignKey('user_management.User', on_delete=models.SET_NULL, null=True, related_name='created_assignments')
    created_at = models.DateTimeField(verbose_name='创建时间', default=timezone.now)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    
    class Meta:
        app_label = 'course_management'
        verbose_name = '作业/考试'
        verbose_name_plural = verbose_name
        ordering = ['-start_time']
        
    def __str__(self):
        return f"{self.course.title} - {self.title} ({self.get_type_display()})"
    
    @property
    def status(self):
        """计算当前状态"""
        now = timezone.now()
        if now < self.start_time:
            return '未开始'
        elif now > self.deadline:
            return '已截止'
        else:
            return '进行中'
