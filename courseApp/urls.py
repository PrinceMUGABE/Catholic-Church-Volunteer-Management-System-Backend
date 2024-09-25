from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_course, name='create_course'),
    path('courses/', views.display_all_courses, name='display_all_courses'),
    path('<int:pk>/', views.find_course_by_id, name='find_course_by_id'),
    path('<int:pk>/update/', views.update_course, name='update_course'),
    path('<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('find_by_name/<str:name>/', views.find_course_by_name, name='find_course_by_name'),
    path('total/', views.get_total_number_of_courses, name='get_total_number_of_courses'),
    path('trends/<str:period>/', views.get_course_trends, name='get_course_trends'),
    path('download/pdf/', views.download_courses_pdf, name='download_courses_pdf'),
    path('download/excel/', views.download_courses_excel, name='download_courses_excel'),
]
