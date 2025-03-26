from django.urls import path
from . import views

urlpatterns = [
    path('insert_face/', views.insert_face, name='insert_face'),
    path('batch_insert_faces/', views.batch_insert_faces, name='batch_insert_faces'),
    path('check_attendance/', views.check_attendance, name='check_attendance'),
    path('download_attendance_file/', views.download_attendance_file, name='download_attendance_file'),
] 