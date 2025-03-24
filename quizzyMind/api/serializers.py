from rest_framework import serializers
from .models import Category, Quiz, Question, Option, QuizSubmission, QuizSubmissionAnswer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    
    class Meta:
        model = Quiz
        fields = '__all__'

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'option_text', 'is_correct']

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
    selected_option = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all())

    class Meta:
        model = QuizSubmissionAnswer
        fields = ["submission", "question", "selected_option"]