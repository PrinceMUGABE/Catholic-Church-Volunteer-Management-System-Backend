from rest_framework import serializers
from .models import Exam, Question

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'answer', 'marks', 'exam']

class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'course', 'created_by', 'created_date', 'total_marks', 'questions']
