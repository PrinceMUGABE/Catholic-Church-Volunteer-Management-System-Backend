
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('userAccountApp.urls')),
    path('task/', include('taskApp.urls')),
    path('volunteer/', include('volunteerApp.urls')),
    path('course/', include('courseApp.urls')),
    path('exam/', include('examApp.urls')),
    path('learner/', include('learnApp.urls')),
    
]
