import io
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Learner
from .serializers import LearnerSerializer
import io
import xlsxwriter
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_learner(request):
    data = request.data
    submitted_answers = data.pop('submitted_answers', [])
    data['user'] = request.user.id
    serializer = LearnerSerializer(data=data)
    if serializer.is_valid():
        learner = serializer.save()
        learner.calculate_achieved_marks(submitted_answers)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def display_all_learners(request):
    learners = Learner.objects.all()
    serializer = LearnerSerializer(learners, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learner_by_id(request, learner_id):
    try:
        learner = Learner.objects.get(id=learner_id)
    except Learner.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = LearnerSerializer(learner)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learners_by_firstname(request, firstname):
    learners = Learner.objects.filter(firstname__icontains=firstname)
    serializer = LearnerSerializer(learners, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learners_by_lastname(request, lastname):
    learners = Learner.objects.filter(lastname__icontains=lastname)
    serializer = LearnerSerializer(learners, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_learner(request, learner_id):
    try:
        learner = Learner.objects.get(id=learner_id)
    except Learner.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    data = request.data
    submitted_answers = data.pop('submitted_answers', [])
    data['user'] = learner.user.id
    serializer = LearnerSerializer(learner, data=data, partial=True)
    if serializer.is_valid():
        learner = serializer.save()
        learner.calculate_achieved_marks(submitted_answers)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_learner(request, learner_id):
    try:
        learner = Learner.objects.get(id=learner_id)
    except Learner.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    learner.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learners_by_status(request, status):
    learners = Learner.objects.filter(status=status)
    serializer = LearnerSerializer(learners, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_total_learners(request):
    count = Learner.objects.count()
    return Response({'total_learners': count})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_total_learners_by_status(request, status):
    count = Learner.objects.filter(status=status).count()
    return Response({'total_learners_by_status': count})

# Additional utility functions for trends and reports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
from django.http import HttpResponse

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_learners_pdf(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Title
    elements.append(Table([["Learners Report"]], style=[('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                                        ('FONTSIZE', (0, 0), (-1, -1), 14),
                                                        ('BOTTOMPADDING', (0, 0), (-1, -1), 12)]))

    learners = Learner.objects.all()
    
    # Table data
    data = [["First Name", "Last Name", "Username", "Exam", "Status", "Marks"]]
    for learner in learners:
        data.append([learner.firstname, learner.lastname, learner.user.username, learner.exam.course.name, learner.status, learner.total_achieved_marks])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="learners.pdf"'
    return response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_learners_by_status_pdf(request, status):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Title
    elements.append(Table([[f"Learners Report - {status.capitalize()}"]], style=[('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                                                                 ('FONTSIZE', (0, 0), (-1, -1), 14),
                                                                                 ('BOTTOMPADDING', (0, 0), (-1, -1), 12)]))

    learners = Learner.objects.filter(status=status)
    
    # Table data
    data = [["First Name", "Last Name", "Username", "Exam", "Status", "Marks"]]
    for learner in learners:
        data.append([learner.firstname, learner.lastname, learner.user.username, learner.exam.course.name, learner.status, learner.total_achieved_marks])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="learners_{status}.pdf"'
    return response



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_learners_excel(request):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    learners = Learner.objects.all()
    
    worksheet.write('A1', 'First Name')
    worksheet.write('B1', 'Last Name')
    worksheet.write('C1', 'Phone')
    worksheet.write('D1', 'Email')
    worksheet.write('E1', 'Exam')
    worksheet.write('F1', 'Total Marks')
    worksheet.write('G1', 'Status')
    worksheet.write('H1', 'Created Date')

    row = 1
    for learner in learners:
        worksheet.write(row, 0, learner.firstname)
        worksheet.write(row, 1, learner.lastname)
        worksheet.write(row, 2, learner.phone)
        worksheet.write(row, 3, learner.email)
        worksheet.write(row, 4, learner.exam.course.name)
        worksheet.write(row, 5, learner.total_achieved_marks)
        worksheet.write(row, 6, learner.status)
        worksheet.write(row, 7, learner.created_date.strftime('%Y-%m-%d %H:%M:%S'))
        row += 1

    workbook.close()

    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="learners.xlsx"'
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_learners_by_status_excel(request, status):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    learners = Learner.objects.filter(status=status)
    
    worksheet.write('A1', 'First Name')
    worksheet.write('B1', 'Last Name')
    worksheet.write('C1', 'Phone')
    worksheet.write('D1', 'Email')
    worksheet.write('E1', 'Exam')
    worksheet.write('F1', 'Total Marks')
    worksheet.write('G1', 'Status')
    worksheet.write('H1', 'Created Date')

    row = 1
    for learner in learners:
        worksheet.write(row, 0, learner.firstname)
        worksheet.write(row, 1, learner.lastname)
        worksheet.write(row, 2, learner.phone)
        worksheet.write(row, 3, learner.email)
        worksheet.write(row, 4, learner.exam.course.name)
        worksheet.write(row, 5, learner.total_achieved_marks)
        worksheet.write(row, 6, learner.status)
        worksheet.write(row, 7, learner.created_date.strftime('%Y-%m-%d %H:%M:%S'))
        row += 1

    workbook.close()

    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="learners_{status}.xlsx"'
    return response
