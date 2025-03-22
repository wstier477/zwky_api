from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.utils import timezone

from .models import Course, CourseTime, StudentCourse, CourseAnnouncement, Assignment
from .serializers import (
    CourseSerializer, CourseDetailSerializer, CourseTimeSerializer,
    CourseAnnouncementSerializer, AssignmentSerializer
)
from user_management.utils import api_response, ErrorCode

class CourseListView(APIView):
    """课程列表视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取用户有权限查看的所有课程"""
        user = request.user
        courses = []
        
        if user.role == 'teacher':
            # 如果是教师，获取该教师教授的课程
            try:
                teacher = user.teacher_profile
                courses = Course.objects.filter(teacher=teacher)
            except:
                return api_response(
                    code=404,
                    message="未找到教师信息",
                    data=None
                )
        elif user.role == 'student':
            # 如果是学生，获取该学生选择的课程
            try:
                student = user.student_profile
                student_courses = StudentCourse.objects.filter(student=student)
                courses = [sc.course for sc in student_courses]
            except:
                return api_response(
                    code=404,
                    message="未找到学生信息",
                    data=None
                )
        else:
            return api_response(
                code=403,
                message="用户角色不正确",
                data=None
            )
            
        serializer = CourseSerializer(courses, many=True)
        
        return api_response(
            code=200,
            message="获取成功",
            data={
                "total": len(serializer.data),
                "items": serializer.data
            }
        )

class CourseDetailView(APIView):
    """课程详情视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """获取特定课程的详细信息"""
        user = request.user
        
        try:
            # 获取课程
            course = get_object_or_404(Course, course_id=pk)
            
            # 检查用户权限
            if user.role == 'teacher':
                try:
                    teacher = user.teacher_profile
                    if course.teacher != teacher:
                        return api_response(
                            code=403,
                            message="无权查看此课程",
                            data=None
                        )
                except:
                    return api_response(
                        code=404,
                        message="未找到教师信息",
                        data=None
                    )
            elif user.role == 'student':
                try:
                    student = user.student_profile
                    if not StudentCourse.objects.filter(student=student, course=course).exists():
                        return api_response(
                            code=403,
                            message="无权查看此课程",
                            data=None
                        )
                except:
                    return api_response(
                        code=404,
                        message="未找到学生信息",
                        data=None
                    )
            else:
                return api_response(
                    code=403,
                    message="用户角色不正确",
                    data=None
                )
                
            serializer = CourseDetailSerializer(course)
            
            return api_response(
                code=200,
                message="获取成功",
                data=serializer.data
            )
        except Exception as e:
            return api_response(
                code=500,
                message=f"服务器错误: {str(e)}",
                data=None
            )

class CourseTimeView(APIView):
    """课程时间视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id):
        """获取课程的所有时间安排"""
        try:
            # 获取课程
            course = get_object_or_404(Course, course_id=course_id)
            
            # 获取课程时间
            course_times = CourseTime.objects.filter(course=course)
            serializer = CourseTimeSerializer(course_times, many=True)
            
            return api_response(
                code=200,
                message="获取成功",
                data={
                    "total": len(serializer.data),
                    "items": serializer.data
                }
            )
        except Exception as e:
            return api_response(
                code=500,
                message=f"服务器错误: {str(e)}",
                data=None
            )
    
    def post(self, request, course_id):
        """添加课程时间安排"""
        try:
            # 验证用户是否为教师
            user = request.user
            if user.role != 'teacher':
                return api_response(
                    code=403,
                    message="只有教师可以添加课程时间",
                    data=None
                )
                
            # 获取课程
            course = get_object_or_404(Course, course_id=course_id)
            
            # 验证教师是否为课程的教师
            teacher = user.teacher_profile
            if course.teacher != teacher:
                return api_response(
                    code=403,
                    message="只有课程的任课教师可以添加课程时间",
                    data=None
                )
                
            # 创建课程时间
            data = request.data.copy()
            data['course'] = course.course_id
            data['teacher'] = teacher.teacher_id
            
            serializer = CourseTimeSerializer(data=data)
            if serializer.is_valid():
                course_time = serializer.save()
                return api_response(
                    code=200,
                    message="添加成功",
                    data=serializer.data
                )
            else:
                return api_response(
                    code=400,
                    message=str(serializer.errors),
                    data=None
                )
        except Exception as e:
            return api_response(
                code=500,
                message=f"服务器错误: {str(e)}",
                data=None
            )

class CourseAnnouncementView(APIView):
    """课程公告视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id):
        """获取课程的所有公告"""
        try:
            # 获取课程
            course = get_object_or_404(Course, course_id=course_id)
            
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            announcement_type = request.GET.get('type')
            
            # 构建查询
            query = Q(course=course)
            if announcement_type:
                query &= Q(type=announcement_type)
                
            # 获取公告并分页
            announcements = CourseAnnouncement.objects.filter(query)
            total = announcements.count()
            
            # 简单分页
            start = (page - 1) * size
            end = start + size
            announcements = announcements[start:end]
            
            serializer = CourseAnnouncementSerializer(announcements, many=True)
            
            return api_response(
                code=200,
                message="获取成功",
                data={
                    "total": total,
                    "items": serializer.data
                }
            )
        except Exception as e:
            return api_response(
                code=500,
                message=f"服务器错误: {str(e)}",
                data=None
            )
    
    def post(self, request, course_id):
        """发布课程公告"""
        try:
            # 验证用户是否为教师
            user = request.user
            if user.role != 'teacher':
                return api_response(
                    code=403,
                    message="只有教师可以发布公告",
                    data=None
                )
                
            # 获取课程
            course = get_object_or_404(Course, course_id=course_id)
            
            # 验证教师是否为课程的教师
            teacher = user.teacher_profile
            if course.teacher != teacher:
                return api_response(
                    code=403,
                    message="只有课程的任课教师可以发布公告",
                    data=None
                )
                
            # 创建公告
            data = request.data.copy()
            data['course'] = course.course_id
            data['created_by'] = user.id
            
            serializer = CourseAnnouncementSerializer(data=data)
            if serializer.is_valid():
                announcement = serializer.save()
                return api_response(
                    code=200,
                    message="发布成功",
                    data=serializer.data
                )
            else:
                return api_response(
                    code=400,
                    message=str(serializer.errors),
                    data=None
                )
        except Exception as e:
            return api_response(
                code=500,
                message=f"服务器错误: {str(e)}",
                data=None
            )

class AssignmentView(APIView):
    """作业与考试视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id):
        """获取课程的所有作业和考试"""
        try:
            # 获取课程
            course = get_object_or_404(Course, course_id=course_id)
            
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 10))
            assignment_type = request.GET.get('type')
            status_filter = request.GET.get('status')
            
            # 构建查询
            query = Q(course=course)
            if assignment_type:
                query &= Q(type=assignment_type)
                
            # 获取作业并分页
            assignments = Assignment.objects.filter(query)
            
            # 状态过滤 (需要在Python中处理，因为status是动态计算的)
            if status_filter:
                now = timezone.now()
                if status_filter == '未开始':
                    assignments = assignments.filter(start_time__gt=now)
                elif status_filter == '进行中':
                    assignments = assignments.filter(start_time__lte=now, deadline__gt=now)
                elif status_filter == '已截止':
                    assignments = assignments.filter(deadline__lte=now)
            
            total = assignments.count()
            
            # 简单分页
            start = (page - 1) * size
            end = start + size
            assignments = assignments[start:end]
            
            serializer = AssignmentSerializer(assignments, many=True)
            
            return api_response(
                code=200,
                message="获取成功",
                data={
                    "total": total,
                    "items": serializer.data
                }
            )
        except Exception as e:
            return api_response(
                code=500,
                message=f"服务器错误: {str(e)}",
                data=None
            )
    
    def post(self, request, course_id):
        """发布作业/考试"""
        try:
            # 验证用户是否为教师
            user = request.user
            if user.role != 'teacher':
                return api_response(
                    code=403,
                    message="只有教师可以发布作业/考试",
                    data=None
                )
                
            # 获取课程
            course = get_object_or_404(Course, course_id=course_id)
            
            # 验证教师是否为课程的教师
            teacher = user.teacher_profile
            if course.teacher != teacher:
                return api_response(
                    code=403,
                    message="只有课程的任课教师可以发布作业/考试",
                    data=None
                )
                
            # 创建作业/考试
            data = request.data.copy()
            data['course'] = course.course_id
            data['created_by'] = user.id
            
            serializer = AssignmentSerializer(data=data)
            if serializer.is_valid():
                assignment = serializer.save()
                return api_response(
                    code=200,
                    message="发布成功",
                    data=serializer.data
                )
            else:
                return api_response(
                    code=400,
                    message=str(serializer.errors),
                    data=None
                )
        except Exception as e:
            return api_response(
                code=500,
                message=f"服务器错误: {str(e)}",
                data=None
            )
