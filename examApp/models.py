from django.db import models
from django.conf import settings
from courseApp.models import Course

class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    total_marks = models.IntegerField(default=0)  # Field to store the sum of question marks

    def update_total_marks(self):
        self.total_marks = self.questions.aggregate(models.Sum('marks'))['marks__sum'] or 0
        self.save()

    def __str__(self):
        return f"Exam for {self.course.name} by {self.created_by.username}"

class Question(models.Model):
    exam = models.ForeignKey(Exam, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    answer = models.TextField()
    marks = models.IntegerField()  # Renamed to 'marks'

    def __str__(self):
        return self.question_text

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.exam.update_total_marks()
