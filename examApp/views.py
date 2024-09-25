from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Exam, Question
from .serializers import ExamSerializer, QuestionSerializer
from django.db.models import Sum
import io
import xlsxwriter
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_exam(request):
    data = request.data
    questions_data = data.pop('questions', [])

    # Create and validate the exam serializer
    exam_serializer = ExamSerializer(data=data)
    if exam_serializer.is_valid():
        exam = exam_serializer.save(created_by=request.user)

        # Process each question and save them with the exam ID
        saved_questions = []
        for question_data in questions_data:
            question_data['exam'] = exam.id  # Assign the exam ID to each question
            question_serializer = QuestionSerializer(data=question_data)
            if question_serializer.is_valid():
                question_serializer.save()
                saved_questions.append(question_serializer.data)
            else:
                # Rollback exam creation if question validation fails
                exam.delete()
                return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update total_marks based on saved questions
        exam.update_total_marks()

        # Return the serialized exam with saved questions
        response_data = {
            'id': exam.id,
            'questions': saved_questions,
            'created_date': exam.created_date,
            'total_marks': exam.total_marks,
            'course': exam.course.id,  # Assuming Exam has a ForeignKey field 'course'
            'created_by': exam.created_by.id,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    return Response(exam_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def display_all_exams(request):
    exams = Exam.objects.all()
    serializer = ExamSerializer(exams, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exam_by_id(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = ExamSerializer(exam)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exams_by_course(request, course_id):
    exams = Exam.objects.filter(course_id=course_id)
    serializer = ExamSerializer(exams, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_exam(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = request.data
    questions_data = data.pop('questions', [])

    # Update exam details (excluding questions)
    exam_serializer = ExamSerializer(exam, data=data, partial=True)
    if exam_serializer.is_valid():
        exam_serializer.save()

        # Track existing question IDs to avoid duplicates
        existing_question_ids = {q.id for q in exam.questions.all()}

        for question_data in questions_data:
            question_id = question_data.get('id')
            if question_id and question_id in existing_question_ids:
                # Update existing question
                try:
                    question = Question.objects.get(id=question_id, exam=exam)
                    question_serializer = QuestionSerializer(question, data=question_data, partial=True)
                    if question_serializer.is_valid():
                        question_serializer.save()
                    else:
                        return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except Question.DoesNotExist:
                    return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Create new question
                question_data['exam'] = exam.id
                question_serializer = QuestionSerializer(data=question_data)
                if question_serializer.is_valid():
                    question_serializer.save()
                else:
                    return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update total marks based on the current questions
        exam.update_total_marks()

        # Return the serialized exam with updated questions
        response_data = {
            'id': exam.id,
            'questions': QuestionSerializer(exam.questions.all(), many=True).data,
            'created_date': exam.created_date,
            'total_marks': exam.total_marks,
            'course': exam.course.id,
            'created_by': exam.created_by.id,
        }
        return Response(response_data)
    return Response(exam_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_exam(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    exam.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exams_by_created_by(request, user_id):
    exams = Exam.objects.filter(created_by_id=user_id)
    serializer = ExamSerializer(exams, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def extend_exam_questions(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = ExamSerializer(exam)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def total_number_of_exams(request):
    count = Exam.objects.count()
    return Response({'total_exams': count})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def total_number_of_exams_by_course(request, course_id):
    count = Exam.objects.filter(course_id=course_id).count()
    return Response({'total_exams_in_course': count})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def total_number_of_questions_in_exam(request, exam_id):
    count = Question.objects.filter(exam_id=exam_id).count()
    return Response({'total_questions_in_exam': count})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_question_by_id(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = QuestionSerializer(question)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    data = request.data
    serializer = QuestionSerializer(question, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        question.exam.update_total_marks()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Placeholder for increase/decrease functions

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_exams_pdf(request, course_id):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    exams = Exam.objects.filter(course_id=course_id)
    
    p.drawString(100, 750, "Exams Report")
    y = 700
    for exam in exams:
        p.drawString(100, y, f"Exam for {exam.course.name}, Created By: {exam.created_by.username}, Created Date: {exam.created_date.strftime('%Y-%m-%d %H:%M:%S')}, Total Marks: {exam.total_marks}")
        y -= 20
        for question in exam.questions.all():
            p.drawString(120, y, f"Q: {question.question_text}, A: {question.answer}, Marks: {question.total_marks}")
            y -= 20
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{exam.course.name}.pdf"'
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_exams_excel(request, course_id):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    exams = Exam.objects.filter(course_id=course_id)
    
    worksheet.write('A1', 'Course Name')
    worksheet.write('B1', 'Created By')
    worksheet.write('C1', 'Created Date')
    worksheet.write('D1', 'Total Marks')
    worksheet.write('E1', 'Question')
    worksheet.write('F1', 'Answer')
    worksheet.write('G1', 'Marks')

    row = 1
    for exam in exams:
        for question in exam.questions.all():
            worksheet.write(row, 0, exam.course.name)
            worksheet.write(row, 1, exam.created_by.username)
            worksheet.write(row, 2, exam.created_date.strftime('%Y-%m-%d %H:%M:%S'))
            worksheet.write(row, 3, exam.total_marks)
            worksheet.write(row, 4, question.question_text)
            worksheet.write(row, 5, question.answer)
            worksheet.write(row, 6, question.total_marks)
            row += 1

    workbook.close()
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{exam.course.name}.xlsx"'
    return response
