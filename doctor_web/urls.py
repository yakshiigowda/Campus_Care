from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('all-patients/', views.view_all_patients, name='view_all_patients'),
    path('delete-student/<str:usn>/', views.delete_student, name='delete_student'),
    path('delete-teacher/<str:isn>/', views.delete_teacher, name='delete_teacher'),
]
