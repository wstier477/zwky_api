from rest_framework import serializers
from .models import Course, CourseResource

class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_id', 'title', 'teacher', 'description', 'location', 'system', 'schedule', 'semester']

class CourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class CourseResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseResource
        fields = ['id', 'name', 'type', 'description', 'upload_time']

class CourseResourceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseResource
        fields = '__all__' 