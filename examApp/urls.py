from django.urls import path
from .views import (
    create_exam, display_all_exams, get_exam_by_id, get_exams_by_course, 
    update_exam, delete_exam, get_exams_by_created_by, extend_exam_questions, 
    total_number_of_exams, total_number_of_exams_by_course, total_number_of_questions_in_exam, 
    update_question, download_exams_pdf, download_exams_excel, get_question_by_id
)

urlpatterns = [
    path('create/', create_exam, name='create_exam'),
    path('exams/', display_all_exams, name='display_all_exams'),
    path('<int:exam_id>/', get_exam_by_id, name='get_exam_by_id'),
    path('course/<int:course_id>/', get_exams_by_course, name='get_exams_by_course'),
    path('update/<int:exam_id>/', update_exam, name='update_exam'),
    path('delete/<int:exam_id>/', delete_exam, name='delete_exam'),
    path('created_by/<int:user_id>/', get_exams_by_created_by, name='get_exams_by_created_by'),
    path('extend/<int:exam_id>/', extend_exam_questions, name='extend_exam_questions'),
    path('total/', total_number_of_exams, name='total_number_of_exams'),
    path('total_by_course/<int:course_id>/', total_number_of_exams_by_course, name='total_number_of_exams_by_course'),
    path('total_questions/<int:exam_id>/', total_number_of_questions_in_exam, name='total_number_of_questions_in_exam'),
    path('update_question/<int:question_id>/', update_question, name='update_question'),
    path('download/pdf/<int:course_id>/', download_exams_pdf, name='download_exams_pdf'),
    path('download/excel/<int:course_id>/', download_exams_excel, name='download_exams_excel'),
    path('question/<int:question_id>/', get_question_by_id, name='get_question_by_id'),
]
