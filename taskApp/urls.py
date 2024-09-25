from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('update/<int:pk>/', views.task_update, name='task_update'),
    path('delete/<int:pk>/', views.task_delete, name='task_delete'),
    path('name/<str:name>/', views.task_by_name, name='task_by_name'),
    path('created_date/<str:created_date>/', views.tasks_by_created_date, name='tasks_by_created_date'),
    path('qualification/<str:qualification>/', views.tasks_by_qualification, name='tasks_by_qualification'),
    path('created_by/<str:username>/', views.tasks_by_created_by, name='tasks_by_created_by'),
    
    path('total/', views.total_tasks, name='total_tasks'),
    path('trend/<str:period>/', views.tasks_trend, name='tasks_trend'),
    path('download/pdf/', views.download_tasks_pdf, name='download_tasks_pdf'),
    path('download/excel/', views.download_tasks_excel, name='download_tasks_excel'),
]
