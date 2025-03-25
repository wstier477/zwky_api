from django.urls import path
from .views import CourseListView, CourseDetailView
from .views import CourseResourceListView, ResourceDetailView, ResourceDownloadView

urlpatterns = [
    # 课程相关接口
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<int:course_id>/', CourseDetailView.as_view(), name='course_detail'),
    
    # 课程资源相关接口
    path('courses/<int:course_id>/resources/', CourseResourceListView.as_view(), name='course_resources'),
    path('resources/<int:resource_id>/', ResourceDetailView.as_view(), name='resource_detail'),
    path('resources/<int:resource_id>/download/', ResourceDownloadView.as_view(), name='resource_download'),
] 