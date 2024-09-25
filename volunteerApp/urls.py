from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.volunteer_create, name='volunteer_create'),
    path('update/<int:pk>/', views.volunteer_update, name='volunteer_update'),
    path('delete/<int:pk>/', views.volunteer_delete, name='volunteer_delete'),
    path('volunteer/<int:pk>/', views.volunteer_detail, name='volunteer_detail'),
    path('volunteers/', views.volunteer_list, name='volunteer_list'),
    path('firstname/<str:first_name>/', views.volunteer_by_first_name, name='volunteer_by_first_name'),
    path('lastname/<str:last_name>/', views.volunteer_by_last_name, name='volunteer_by_last_name'),
    path('task/<str:task_name>/', views.volunteer_by_task, name='volunteer_by_task'),
    path('phone/<str:phone_number>/', views.volunteer_by_phone, name='volunteer_by_phone'),
    path('total_by_status/', views.total_volunteers_by_status, name='total_volunteers_by_status'),
    path('trend/<str:period>/', views.volunteers_trend, name='volunteers_trend'),
    path('download/pdf/', views.download_volunteers_pdf, name='download_volunteers_pdf'),
    path('download/excel/', views.download_volunteers_excel, name='download_volunteers_excel'),
]
