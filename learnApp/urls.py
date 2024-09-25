from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_learner, name='create_learner'),
    path('learners/', views.display_all_learners, name='display_all_learners'),
    path('<int:learner_id>/', views.get_learner_by_id, name='get_learner_by_id'),
    path('firstname/<str:firstname>/', views.get_learners_by_firstname, name='get_learners_by_firstname'),
    path('lastname/<str:lastname>/', views.get_learners_by_lastname, name='get_learners_by_lastname'),
    path('update/<int:learner_id>/', views.update_learner, name='update_learner'),
    path('delete/<int:learner_id>/', views.delete_learner, name='delete_learner'),
    path('status/<str:status>/', views.get_learners_by_status, name='get_learners_by_status'),
    path('total/', views.get_total_learners, name='get_total_learners'),
    path('total/status/<str:status>/', views.get_total_learners_by_status, name='get_total_learners_by_status'),
    
    
    path('download/pdf/', views.download_learners_pdf, name='download_learners_pdf'),
    path('download/status/pdf/<str:status>/', views.download_learners_by_status_pdf, name='download_learners_by_status_pdf'),
    path('download/excel/', views.download_learners_excel, name='download_learners_excel'),
    path('download/status/excel/<str:status>/', views.download_learners_by_status_excel, name='download_learners_by_status_excel'),
]
