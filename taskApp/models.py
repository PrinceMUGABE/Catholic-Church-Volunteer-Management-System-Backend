from django.db import models
from django.conf import settings

class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    qualification = models.TextField()
    due_date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    total_volunteers_number_accepted = models.DecimalField(max_digits=10, decimal_places=2, null=True)


    def __str__(self):
        return self.name
