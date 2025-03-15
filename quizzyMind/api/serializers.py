from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['option_text']
    
class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']

class QuizSubmisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSubmission
        fields = ['id', 'user', 'quiz', 'score', 'created_at', 'updated_at']

class QuizSubmissionAnswerSerializer(serializers.ModelSerializer):
    selected_option = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = QuizSubmissionAnswer
        fields = ["submission", "question", "selected_question"]