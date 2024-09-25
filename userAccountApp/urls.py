from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', views.home, name='home'),
    path('users/', views.users, name='users'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('user/username/<str:username>/', views.user_by_username, name='user_by_username'),
    path('user/email/<str:email>/', views.user_by_email, name='user_by_email'),
    path('user/phone/<str:phone>/', views.user_by_phone, name='user_by_phone'),
    path('users/role/<str:role>/', views.users_by_role, name='users_by_role'),
    path('user/update/<int:user_id>/', views.update_user, name='update_user'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('total_users/', views.total_users, name='total_users'),
    path('user_growth/', views.user_growth, name='user_growth'),
    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
