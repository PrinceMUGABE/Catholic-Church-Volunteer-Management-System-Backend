from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import HttpResponse, JsonResponse
from .models import CustomUser
from .serializers import CustomUserSerializer
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return HttpResponse("Welcome to Quran Catholic church voulunteermanagement system Backend!")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users(request):
    users = CustomUser.objects.all()
    serializer = CustomUserSerializer(users, many=True)
    return JsonResponse({'users': serializer.data})

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    username = request.data.get('username')
    email = request.data.get('email')
    role = 'user'
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    if not all([username, email, password, confirm_password]):
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    hashed_password = make_password(password)
    try:
        user = CustomUser.objects.create(username=username, email=email, role=role, password=hashed_password)
        subject = 'User Registration Confirmation'
        message = (f'Hello, {username},\n'
                   'Your account to CATHOLIC CHURCH VOLUNTEER MANAGEMENY SYSTEM has successfully created \n'
                   'Login with the credentials:\n'
                   f'Username: {username}\nPassword: {password}\n\n'
                   'Kindly do not reply this mail')
        
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)
    
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    serializer = CustomUserSerializer(user)
    return JsonResponse(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_by_username(request, username):
    user = get_object_or_404(CustomUser, username=username)
    serializer = CustomUserSerializer(user)
    return JsonResponse(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_by_email(request, email):
    user = get_object_or_404(CustomUser, email=email)
    serializer = CustomUserSerializer(user)
    return JsonResponse(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_by_phone(request, phone):
    user = get_object_or_404(CustomUser, phone=phone)
    serializer = CustomUserSerializer(user)
    return JsonResponse(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_by_role(request, role):
    users = CustomUser.objects.filter(role=role)
    serializer = CustomUserSerializer(users, many=True)
    return JsonResponse({'users': serializer.data})

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    data = request.data
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.phone = data.get('phone', user.phone)
    user.role = data.get('role', user.role)
    if 'password' in data:
        user.password = make_password(data['password'])
    user.save()
    return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get('email')
    user = get_object_or_404(CustomUser, email=email)
    new_password = request.data.get('new_password')
    user.password = make_password(new_password)
    user.save()
    return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def total_users(request):
    count = CustomUser.objects.count()
    return JsonResponse({'total_users': count})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_growth(request):
    today = datetime.today()
    one_month_ago = today - timedelta(days=30)
    two_months_ago = one_month_ago - timedelta(days=30)

    current_month_users = CustomUser.objects.filter(created_date__gte=one_month_ago).count()
    previous_month_users = CustomUser.objects.filter(created_date__gte=two_months_ago, created_date__lt=one_month_ago).count()

    growth = current_month_users - previous_month_users

    return JsonResponse({'current_month_users': current_month_users, 'previous_month_users': previous_month_users, 'growth': growth})



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)


