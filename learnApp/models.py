from django.db import models
from django.conf import settings
from examApp.models import Exam, Question

class Learner(models.Model):
    STATUS_CHOICES = [
        ('succeded', 'Succeded'),
        ('failed', 'Failed'),
    ]

    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    total_achieved_marks = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='failed')
    created_date = models.DateTimeField(auto_now_add=True)

    def calculate_status(self):
        total_marks = self.exam.total_marks
        if total_marks > 0:
            percentage = (self.total_achieved_marks / total_marks) * 100
            self.status = 'succeded' if percentage >= 50 else 'failed'
        else:
            self.status = 'failed'
        self.save()

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    def calculate_achieved_marks(self, submitted_answers):
        total_achieved_marks = 0
        for answer in submitted_answers:
            try:
                question = Question.objects.get(id=answer['question_id'])
                if question.answer == answer['submitted_answer']:
                    total_achieved_marks += question.marks
            except Question.DoesNotExist:
                continue
        self.total_achieved_marks = total_achieved_marks
        self.calculate_status()
