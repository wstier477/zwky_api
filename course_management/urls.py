from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/<str:course_id>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/<str:course_id>/resources/', views.CourseResourceListView.as_view(), name='course-resources'),
    path('resources/<int:resource_id>/', views.ResourceDetailView.as_view(), name='resource-detail'),
    path('resources/<int:resource_id>/download/', views.ResourceDownloadView.as_view(), name='resource-download'),
    path('courses/<int:course_id>/students/info/', views.CourseStudentInfoView.as_view(), name='course-student-info'),
] 