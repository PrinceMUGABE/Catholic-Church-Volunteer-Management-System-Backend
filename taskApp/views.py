from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Task
from .serializers import TaskSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET'])
def task_list(request):
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def task_create(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    serializer = TaskSerializer(task)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    data = request.data
    data['created_by'] = task.created_by.id  # Ensure the creator doesn't change
    serializer = TaskSerializer(task, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def task_by_name(request, name):
    tasks = Task.objects.filter(name=name)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tasks_by_created_date(request, created_date):
    tasks = Task.objects.filter(created_date__date=created_date)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tasks_by_qualification(request, qualification):
    tasks = Task.objects.filter(qualification__contains=qualification)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tasks_by_created_by(request, username):
    user = get_object_or_404(User, username=username)
    tasks = Task.objects.filter(created_by=user)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


'''
    REPORT
'''

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def total_tasks(request):
    total = Task.objects.count()
    return Response({'total_tasks': total})


from django.db.models import Count
from django.utils.timezone import now, timedelta

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tasks_trend(request, period):
    periods = {
        'day': 1,
        'week': 7,
        'month': 30,
        'three_months': 90,
        'six_months': 180,
        'year': 365,
        'three_years': 3*365,
        'five_years': 5*365,
        'ten_years': 10*365,
    }
    
    if period not in periods:
        return Response({'error': 'Invalid period'}, status=status.HTTP_400_BAD_REQUEST)
    
    end_date = now()
    start_date = end_date - timedelta(days=periods[period])
    
    tasks = Task.objects.filter(created_date__range=(start_date, end_date))
    total_tasks = tasks.count()
    
    return Response({
        'period': period,
        'total_tasks': total_tasks,
    })





import io
import xlsxwriter
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework.decorators import api_view
from .models import Task

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_tasks_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    tasks = Task.objects.all()
    
    p.drawString(100, 750, "Tasks Report")
    y = 700
    for task in tasks:
        p.drawString(100, y, f"Task: {task.name}, Created By: {task.created_by.username}, Due Date: {task.due_date}")
        y -= 20
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tasks_report.pdf"'
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_tasks_excel(request):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    tasks = Task.objects.all()
    
    worksheet.write('A1', 'Task Name')
    worksheet.write('B1', 'Created By')
    worksheet.write('C1', 'Created Date')
    worksheet.write('D1', 'Description')
    worksheet.write('E1', 'Qualification')
    worksheet.write('F1', 'Due Date')

    row = 1
    for task in tasks:
        worksheet.write(row, 0, task.name)
        worksheet.write(row, 1, task.created_by.username)
        worksheet.write(row, 2, task.created_date.strftime('%Y-%m-%d %H:%M:%S'))
        worksheet.write(row, 3, task.description)
        worksheet.write(row, 4, ', '.join(task.qualification))
        worksheet.write(row, 5, task.due_date.strftime('%Y-%m-%d %H:%M:%S'))
        row += 1

    workbook.close()
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="tasks_report.xlsx"'
    return response

