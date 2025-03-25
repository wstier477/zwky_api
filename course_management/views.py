from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.utils.http import quote
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
import os

from .models import Course, StudentCourse, CourseResource
from .serializers import CourseListSerializer, CourseDetailSerializer, CourseResourceSerializer, CourseResourceDetailSerializer
from user_management.utils import api_response


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 100


class CourseListView(APIView):
    """
    课程列表视图
    获取当前用户相关的课程列表
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request):
        """获取当前用户可查看的课程列表"""
        user = request.user
        
        # 根据用户角色获取对应课程
        if user.role == 'teacher':
            # 教师只能查看自己教授的课程
            try:
                teacher = user.teacher_profile
                courses = Course.objects.filter(teacher=teacher)
            except:
                courses = Course.objects.none()
        elif user.role == 'student':
            # 学生只能查看自己选择的课程
            try:
                student = user.student_profile
                student_courses = StudentCourse.objects.filter(student=student)
                course_ids = [sc.course_id for sc in student_courses]
                courses = Course.objects.filter(course_id__in=course_ids)
            except:
                courses = Course.objects.none()
        else:
            # 未知角色，暂时不返回任何课程
            courses = Course.objects.none()
        
        # 使用分页器
        paginator = self.pagination_class()
        paginated_courses = paginator.paginate_queryset(courses, request)
        
        serializer = CourseListSerializer(paginated_courses, many=True)
        
        return api_response(
            code=200,
            message="获取成功",
            data={
                "total": paginator.page.paginator.count,
                "items": serializer.data
            }
        )


class CourseDetailView(APIView):
    """
    课程详情视图
    获取特定课程的详细信息
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id):
        """获取特定课程的详细信息"""
        user = request.user
        
        # 获取课程对象
        course = get_object_or_404(Course, course_id=course_id)
        
        # 检查用户权限
        has_permission = False
        
        if user.role == 'teacher':
            # 教师只能查看自己教授的课程
            try:
                teacher = user.teacher_profile
                has_permission = (course.teacher == teacher)
            except:
                has_permission = False
        elif user.role == 'student':
            # 学生只能查看自己选择的课程
            try:
                student = user.student_profile
                has_permission = StudentCourse.objects.filter(
                    student=student, course=course
                ).exists()
            except:
                has_permission = False
        
        if not has_permission:
            return api_response(
                code=403,
                message="您没有权限访问此课程",
                data=None
            )
        
        serializer = CourseDetailSerializer(course)
        
        return api_response(
            code=200,
            message="获取成功",
            data=serializer.data
        )


class CourseResourceListView(APIView):
    """
    课程资源列表视图
    获取和上传课程资源
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request, course_id):
        """获取课程的资源列表"""
        # 检查课程是否存在
        course = get_object_or_404(Course, course_id=course_id)
        
        # 检查用户权限（必须是课程的教师或学生）
        user = request.user
        has_permission = False
        
        if user.role == 'teacher':
            try:
                teacher = user.teacher_profile
                has_permission = (course.teacher == teacher)
            except:
                has_permission = False
        elif user.role == 'student':
            try:
                student = user.student_profile
                has_permission = StudentCourse.objects.filter(
                    student=student, course=course
                ).exists()
            except:
                has_permission = False
        
        if not has_permission:
            return api_response(
                code=403,
                message="您没有权限访问此课程资源",
                data=None
            )
        
        # 过滤条件
        resource_type = request.query_params.get('type')
        search_query = request.query_params.get('search')
        
        # 查询资源
        resources = CourseResource.objects.filter(course=course)
        
        # 应用过滤条件
        if resource_type:
            resources = resources.filter(type=resource_type)
        
        if search_query:
            resources = resources.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # 分页
        paginator = self.pagination_class()
        paginated_resources = paginator.paginate_queryset(resources, request)
        
        serializer = CourseResourceSerializer(
            paginated_resources, 
            many=True,
            context={'request': request}
        )
        
        return api_response(
            code=200,
            message="获取成功",
            data={
                "total": paginator.page.paginator.count,
                "items": serializer.data
            }
        )
    
    def post(self, request, course_id):
        """上传课程资源"""
        # 检查课程是否存在
        course = get_object_or_404(Course, course_id=course_id)
        
        # 检查用户权限（必须是课程的教师）
        user = request.user
        has_permission = False
        
        if user.role == 'teacher':
            try:
                teacher = user.teacher_profile
                has_permission = (course.teacher == teacher)
            except:
                has_permission = False
        
        if not has_permission:
            return api_response(
                code=403,
                message="您没有权限上传资源到此课程",
                data=None
            )
        
        # 获取上传的文件
        file_obj = request.FILES.get('file')
        if not file_obj:
            return api_response(
                code=400,
                message="未提供文件",
                data=None
            )
        
        # 准备资源数据
        resource_data = {
            'name': request.data.get('name', file_obj.name),
            'type': request.data.get('type', 'document'),  # 默认为文档类型
            'description': request.data.get('description', ''),
            'file': file_obj,
            'size': f"{file_obj.size / 1024:.1f}KB" if file_obj.size < 1024 * 1024 else f"{file_obj.size / (1024 * 1024):.1f}MB",
            'course': course,
            'uploader': user
        }
        
        # 创建资源
        resource = CourseResource.objects.create(**resource_data)
        
        # 序列化返回
        serializer = CourseResourceSerializer(
            resource,
            context={'request': request}
        )
        
        return api_response(
            code=200,
            message="上传成功",
            data=serializer.data
        )


class ResourceDetailView(APIView):
    """
    资源详情视图
    获取和删除资源
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, resource_id):
        """获取资源详情"""
        resource = get_object_or_404(CourseResource, id=resource_id)
        
        # 检查用户权限
        user = request.user
        has_permission = False
        
        if user.role == 'teacher':
            try:
                teacher = user.teacher_profile
                has_permission = (resource.course.teacher == teacher)
            except:
                has_permission = False
        elif user.role == 'student':
            try:
                student = user.student_profile
                has_permission = StudentCourse.objects.filter(
                    student=student, course=resource.course
                ).exists()
            except:
                has_permission = False
        
        if not has_permission:
            return api_response(
                code=403,
                message="您没有权限访问此资源",
                data=None
            )
        
        serializer = CourseResourceDetailSerializer(
            resource,
            context={'request': request}
        )
        
        return api_response(
            code=200,
            message="获取成功",
            data=serializer.data
        )
    
    def delete(self, request, resource_id):
        """删除资源"""
        resource = get_object_or_404(CourseResource, id=resource_id)
        
        # 检查用户权限（必须是资源的上传者或课程教师）
        user = request.user
        has_permission = (resource.uploader == user)
        
        if not has_permission and user.role == 'teacher':
            try:
                teacher = user.teacher_profile
                has_permission = (resource.course.teacher == teacher)
            except:
                pass
        
        if not has_permission:
            return api_response(
                code=403,
                message="您没有权限删除此资源",
                data=None
            )
        
        # 删除文件
        if resource.file and os.path.exists(resource.file.path):
            try:
                os.remove(resource.file.path)
            except:
                pass
        
        # 删除数据库记录
        resource.delete()
        
        return api_response(
            code=200,
            message="删除成功",
            data=None
        )


class ResourceDownloadView(APIView):
    """
    资源下载视图
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, resource_id):
        """下载资源"""
        resource = get_object_or_404(CourseResource, id=resource_id)
        
        # 检查用户权限
        user = request.user
        has_permission = False
        
        if user.role == 'teacher':
            try:
                teacher = user.teacher_profile
                has_permission = (resource.course.teacher == teacher)
            except:
                has_permission = False
        elif user.role == 'student':
            try:
                student = user.student_profile
                has_permission = StudentCourse.objects.filter(
                    student=student, course=resource.course
                ).exists()
            except:
                has_permission = False
        
        if not has_permission:
            return api_response(
                code=403,
                message="您没有权限下载此资源",
                data=None
            )
        
        # 检查文件是否存在
        if not resource.file or not os.path.exists(resource.file.path):
            return api_response(
                code=404,
                message="文件不存在",
                data=None
            )
        
        # 增加下载计数
        resource.download_count += 1
        resource.save()
        
        # 获取文件类型
        file_path = resource.file.path
        
        try:
            # 尝试直接返回文件
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment; filename="{quote(resource.name)}"'
            return response
        except Exception as e:
            # 如果直接返回失败，返回下载链接
            return api_response(
                code=200,
                message="下载链接生成成功",
                data={
                    "downloadUrl": request.build_absolute_uri(resource.file.url)
                }
            )
