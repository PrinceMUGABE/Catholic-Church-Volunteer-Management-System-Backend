import io
import xlsxwriter
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Course
from .serializers import CourseSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request):
    data = request.data
    data['created_by'] = request.user.id

    # Check for duplicate course name
    if Course.objects.filter(name=data['name']).exists():
        return Response({'error': 'Course with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = CourseSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def display_all_courses(request):
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def find_course_by_id(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = CourseSerializer(course)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_course(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    data = request.data
    data['created_by'] = course.created_by.id
    serializer = CourseSerializer(course, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_course(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    course.delete()
    return Response({'message': 'Course deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def find_course_by_name(request, name):
    courses = Course.objects.filter(name__icontains=name)
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_total_number_of_courses(request):
    total_courses = Course.objects.count()
    return Response({'total_courses': total_courses}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_trends(request, period):
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    trends = {
        'day': now - timedelta(days=1),
        'week': now - timedelta(weeks=1),
        'month': now - timedelta(days=30),
        'three_months': now - timedelta(days=90),
        'six_months': now - timedelta(days=180),
        'year': now - timedelta(days=365),
        'three_years': now - timedelta(days=1095),
        'five_years': now - timedelta(days=1825),
        'ten_years': now - timedelta(days=3650),
    }
    
    if period not in trends:
        return Response({'error': 'Invalid period specified'}, status=status.HTTP_400_BAD_REQUEST)

    period_start = trends[period]
    course_trends = Course.objects.filter(created_date__gte=period_start).annotate(num_courses=Count('id'))

    return Response({'num_courses': course_trends.count()}, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def download_courses_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    courses = Course.objects.all()
    
    # Define the table headers and data
    headers = ['Course Name', 'Created By', 'Created Date']
    data = []
    for course in courses:
        data.append([course.name, course.created_by.username, course.created_date.strftime('%Y-%m-%d %H:%M:%S')])

    # Start drawing table
    width, height = letter
    table_width = width - 100
    table_height = height - 150
    cell_width = table_width / len(headers)
    cell_height = 20

    x_offset = 50
    y_offset = height - 100

    # Draw table headers
    for i, header in enumerate(headers):
        p.drawString(x_offset + i * cell_width, y_offset, header)

    # Draw table data
    y_offset -= cell_height
    for row in data:
        for i, cell in enumerate(row):
            p.drawString(x_offset + i * cell_width, y_offset, cell)
        y_offset -= cell_height

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="courses.pdf"'
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_courses_excel(request):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    courses = Course.objects.all()
    
    worksheet.write('A1', 'Name')
    worksheet.write('B1', 'Created By')
    worksheet.write('C1', 'Created Date')

    row = 1
    for course in courses:
        worksheet.write(row, 0, course.name)
        worksheet.write(row, 1, course.created_by.username)
        worksheet.write(row, 2, course.created_date.strftime('%Y-%m-%d %H:%M:%S'))
        row += 1

    workbook.close()
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="courses.xlsx"'
    return response
