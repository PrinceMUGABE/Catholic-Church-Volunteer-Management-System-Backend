from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Volunteer
from .serializers import VolunteerSerializer
from taskApp.models import Task
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def volunteer_create(request):
    serializer = VolunteerSerializer(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def volunteer_update(request, pk):
    volunteer = Volunteer.objects.get(pk=pk)
    serializer = VolunteerSerializer(volunteer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def volunteer_delete(request, pk):
    volunteer = Volunteer.objects.get(pk=pk)
    volunteer.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(['GET'])
def volunteer_detail(request, pk):
    volunteer = Volunteer.objects.get(pk=pk)
    serializer = VolunteerSerializer(volunteer)
    return Response(serializer.data)




@api_view(['GET'])
def volunteer_list(request):
    volunteers = Volunteer.objects.all()
    serializer = VolunteerSerializer(volunteers, many=True)
    return Response(serializer.data)




@api_view(['GET'])
def volunteer_by_first_name(request, first_name):
    volunteers = Volunteer.objects.filter(first_name__icontains=first_name)
    serializer = VolunteerSerializer(volunteers, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def volunteer_by_last_name(request, last_name):
    volunteers = Volunteer.objects.filter(last_name__icontains=last_name)
    serializer = VolunteerSerializer(volunteers, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def volunteer_by_task(request, task_name):
    task = Task.objects.get(name=task_name)
    volunteers = Volunteer.objects.filter(task=task)
    serializer = VolunteerSerializer(volunteers, many=True)
    return Response(serializer.data)





@api_view(['GET'])
def volunteer_by_phone(request, phone_number):
    volunteer = Volunteer.objects.get(phone_number=phone_number)
    serializer = VolunteerSerializer(volunteer)
    return Response(serializer.data)




@api_view(['GET'])
def total_volunteers(request):
    count = Volunteer.objects.count()
    return Response({'total_volunteers': count})

@api_view(['GET'])
def total_volunteers_by_status(request):
    volunteers = Volunteer.objects.values('status').annotate(count=Count('status'))
    return Response(volunteers)

@api_view(['GET'])
def volunteers_trend(request, period):
    now = timezone.now()
    if period == 'day':
        delta = timedelta(days=1)
    elif period == 'week':
        delta = timedelta(weeks=1)
    elif period == 'month':
        delta = timedelta(days=30)
    elif period == 'three_months':
        delta = timedelta(days=90)
    elif period == 'six_months':
        delta = timedelta(days=180)
    elif period == 'year':
        delta = timedelta(days=365)
    elif period == 'three_years':
        delta = timedelta(days=1095)
    elif period == 'five_years':
        delta = timedelta(days=1825)
    elif period == 'ten_years':
        delta = timedelta(days=3650)
    else:
        return Response({'error': 'Invalid period'}, status=status.HTTP_400_BAD_REQUEST)

    end_date = now
    start_date = now - delta
    volunteers = Volunteer.objects.filter(created_date__range=(start_date, end_date)).count()
    return Response({f'volunteers_in_last_{period}': volunteers})


import io
import xlsxwriter
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Volunteer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_volunteers_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    volunteers = Volunteer.objects.all()
    
    p.drawString(100, 750, "Volunteers Report")
    y = 700
    for volunteer in volunteers:
        p.drawString(100, y, f"Volunteer: {volunteer.first_name} {volunteer.last_name}, Task: {volunteer.task.name}, Status: {'Active' if volunteer.status else 'Inactive'}")
        y -= 20
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="volunteers.pdf"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_volunteers_excel(request):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    volunteers = Volunteer.objects.all()
    
    worksheet.write('A1', 'First Name')
    worksheet.write('B1', 'Last Name')
    worksheet.write('C1', 'Phone Number')
    worksheet.write('D1', 'Task')
    worksheet.write('E1', 'Qualification')
    worksheet.write('F1', 'Status')
    worksheet.write('G1', 'Created Date')

    row = 1
    for volunteer in volunteers:
        worksheet.write(row, 0, volunteer.first_name)
        worksheet.write(row, 1, volunteer.last_name)
        worksheet.write(row, 2, volunteer.phone_number)
        worksheet.write(row, 3, volunteer.task.name)
        worksheet.write(row, 4, volunteer.qualification)
        worksheet.write(row, 5, 'Active' if volunteer.status else 'Inactive')
        worksheet.write(row, 6, volunteer.created_date.strftime('%Y-%m-%d %H:%M:%S'))
        row += 1

    workbook.close()
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="volunteers.xlsx"'
    return response
