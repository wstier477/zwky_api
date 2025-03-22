from django.urls import path
from .views import (
    CourseListView, CourseDetailView, CourseTimeView,
    CourseAnnouncementView, AssignmentView
)

urlpatterns = [
    # 课程相关接口
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/times/', CourseTimeView.as_view(), name='course-times'),
    
    # 课程公告接口
    path('courses/<int:course_id>/announcements/', CourseAnnouncementView.as_view(), name='course-announcements'),
    
    # 作业与考试接口
    path('courses/<int:course_id>/assignments/', AssignmentView.as_view(), name='course-assignments'),
] 