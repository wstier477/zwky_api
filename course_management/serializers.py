from rest_framework import serializers
from .models import Course, CourseTime, StudentCourse, CourseResource
from user_management.models import Teacher, User


class TeacherSerializer(serializers.ModelSerializer):
    """教师序列化器"""
    teacher_id = serializers.IntegerField()
    teacher_title = serializers.CharField()
    username = serializers.CharField(source='user.username')
    
    class Meta:
        model = Teacher
        fields = ['teacher_id', 'teacher_title', 'username']


class CourseTimeSerializer(serializers.ModelSerializer):
    """课程时间序列化器"""
    class Meta:
        model = CourseTime
        fields = ['id', 'begin_time', 'end_time']


class CourseListSerializer(serializers.ModelSerializer):
    """课程列表序列化器（简要信息）"""
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    student_count = serializers.SerializerMethodField()
    building = serializers.SerializerMethodField()
    room_number = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['course_id', 'title', 'location', 'building', 'room_number', 
                  'teacher_name', 'student_count', 'system', 'schedule', 'semester']
    
    def get_student_count(self, obj):
        """获取选课学生数量"""
        return obj.student_courses.count()
    
    def get_building(self, obj):
        """获取教学楼"""
        if obj.location and ' ' in obj.location:
            return obj.location.split(' ')[0]
        return ""
    
    def get_room_number(self, obj):
        """获取教室号"""
        if obj.location and ' ' in obj.location:
            return obj.location.split(' ')[1]
        return ""


class CourseDetailSerializer(serializers.ModelSerializer):
    """课程详情序列化器（详细信息）"""
    teacher = TeacherSerializer(read_only=True)
    course_times = CourseTimeSerializer(many=True, read_only=True)
    student_count = serializers.SerializerMethodField()
    building = serializers.SerializerMethodField()
    room_number = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['course_id', 'title', 'description', 'location', 'building', 
                  'room_number', 'system', 'schedule', 'semester', 'teacher', 
                  'course_times', 'student_count']
    
    def get_student_count(self, obj):
        """获取选课学生数量"""
        return obj.student_courses.count()
        
    def get_building(self, obj):
        """获取教学楼"""
        if obj.location and ' ' in obj.location:
            return obj.location.split(' ')[0]
        return ""
    
    def get_room_number(self, obj):
        """获取教室号"""
        if obj.location and ' ' in obj.location:
            return obj.location.split(' ')[1]
        return ""


class UserBriefSerializer(serializers.ModelSerializer):
    """用户简要信息序列化器"""
    userId = serializers.CharField(source='staff_id')
    name = serializers.CharField(source='username')
    
    class Meta:
        model = User
        fields = ['userId', 'name']


class CourseResourceSerializer(serializers.ModelSerializer):
    """课程资源序列化器"""
    uploader = UserBriefSerializer(read_only=True)
    size = serializers.CharField(read_only=True)
    uploadTime = serializers.DateTimeField(source='upload_time', format='%Y-%m-%d %H:%M:%S', read_only=True)
    updateTime = serializers.DateTimeField(source='update_time', format='%Y-%m-%d %H:%M:%S', read_only=True)
    url = serializers.SerializerMethodField()
    downloadCount = serializers.IntegerField(source='download_count', read_only=True)
    
    class Meta:
        model = CourseResource
        fields = ['id', 'name', 'type', 'size', 'uploadTime', 'updateTime', 
                  'uploader', 'url', 'downloadCount', 'description']
    
    def get_url(self, obj):
        """获取资源URL"""
        request = self.context.get('request')
        if request and obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None
        
        
class CourseResourceDetailSerializer(CourseResourceSerializer):
    """课程资源详情序列化器"""
    preview = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    
    class Meta(CourseResourceSerializer.Meta):
        fields = CourseResourceSerializer.Meta.fields + ['preview', 'metadata']
    
    def get_preview(self, obj):
        """获取预览信息"""
        # 简单判断文件类型是否支持预览
        preview_types = ['document', 'image']
        preview_available = obj.type in preview_types
        
        return {
            'available': preview_available,
            'previewUrl': self.get_url(obj) if preview_available else None
        }
    
    def get_metadata(self, obj):
        """获取元数据"""
        # 简单返回一些基础信息
        metadata = {
            'author': obj.uploader.username if obj.uploader else '未知',
            'createTime': obj.upload_time.strftime('%Y-%m-%d') if obj.upload_time else '未知',
        }
        
        # 根据资源类型添加特定信息
        if obj.type == 'document':
            metadata['pageCount'] = 0  # 这里需要实际解析文档获取页数
            
        return metadata 