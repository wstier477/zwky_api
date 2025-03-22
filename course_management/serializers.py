from rest_framework import serializers
from django.utils import timezone

from .models import Course, CourseTime, StudentCourse, ClassCourse, CourseAnnouncement, Assignment
from user_management.models import Student, Teacher
from user_management.serializers import UserSerializer

class TeacherSerializer(serializers.ModelSerializer):
    """教师序列化器"""
    user_info = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ('teacher_id', 'teacher_title', 'user', 'user_info')

class CourseTimeSerializer(serializers.ModelSerializer):
    """课程时间序列化器"""
    class Meta:
        model = CourseTime
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # 格式化时间字段以便于前端显示
        if instance.begin_time:
            data['begin_time_formatted'] = instance.begin_time.strftime('%Y-%m-%d %H:%M')
        if instance.end_time:
            data['end_time_formatted'] = instance.end_time.strftime('%Y-%m-%d %H:%M')
            
        return data

class CourseSerializer(serializers.ModelSerializer):
    """课程序列化器"""
    teacher_info = TeacherSerializer(source='teacher', read_only=True)
    course_times = CourseTimeSerializer(many=True, read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ('course_id', 'title', 'description', 'location', 'system', 
                 'schedule', 'semester', 'teacher', 'teacher_info', 'course_times',
                 'student_count')
    
    def get_student_count(self, obj):
        """获取选课学生数量"""
        return obj.student_courses.count()

class CourseDetailSerializer(CourseSerializer):
    """课程详情序列化器"""
    class Meta(CourseSerializer.Meta):
        # 继承CourseSerializer的所有字段
        pass
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # 处理位置信息
        if instance.location:
            parts = instance.location.split()
            if len(parts) >= 2:
                data['building'] = parts[0]
                data['roomNumber'] = parts[1]
            else:
                data['building'] = instance.location
                data['roomNumber'] = ""
                
        return data

class StudentCourseSerializer(serializers.ModelSerializer):
    """学生课程关系序列化器"""
    course_detail = CourseSerializer(source='course', read_only=True)
    
    class Meta:
        model = StudentCourse
        fields = ('id', 'student', 'course', 'course_detail')

class ClassCourseSerializer(serializers.ModelSerializer):
    """班级课程关系序列化器"""
    course_detail = CourseSerializer(source='course', read_only=True)
    
    class Meta:
        model = ClassCourse
        fields = ('id', 'class_id', 'course', 'course_detail')

class CourseAnnouncementSerializer(serializers.ModelSerializer):
    """课程公告序列化器"""
    type_display = serializers.SerializerMethodField()
    created_by_info = UserSerializer(source='created_by', read_only=True)
    created_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseAnnouncement
        fields = ('id', 'title', 'content', 'type', 'type_display', 'course', 
                 'created_by', 'created_by_info', 'created_at', 'created_at_formatted', 'updated_at')
    
    def get_type_display(self, obj):
        return obj.get_type_display()
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')

class AssignmentSerializer(serializers.ModelSerializer):
    """作业/考试序列化器"""
    type_display = serializers.SerializerMethodField()
    status = serializers.ReadOnlyField()
    created_by_info = UserSerializer(source='created_by', read_only=True)
    start_time_formatted = serializers.SerializerMethodField()
    deadline_formatted = serializers.SerializerMethodField()
    submitted = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = ('id', 'title', 'type', 'type_display', 'description', 'start_time', 
                 'start_time_formatted', 'deadline', 'deadline_formatted', 'status',
                 'full_score', 'course', 'created_by', 'created_by_info', 
                 'created_at', 'updated_at', 'submitted', 'total_students')
    
    def get_type_display(self, obj):
        return obj.get_type_display()
    
    def get_start_time_formatted(self, obj):
        return obj.start_time.strftime('%Y-%m-%d %H:%M')
    
    def get_deadline_formatted(self, obj):
        return obj.deadline.strftime('%Y-%m-%d %H:%M')
    
    def get_submitted(self, obj):
        # 这里应该根据实际的作业提交模型来计算
        # 暂时返回0，后续可以扩展
        return 0
    
    def get_total_students(self, obj):
        return obj.course.student_courses.count() 