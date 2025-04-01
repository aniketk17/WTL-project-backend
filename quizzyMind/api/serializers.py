from rest_framework import serializers
from .models import *
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
        fields = ['option_text']

class QuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    correctAnswer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['text', 'options', 'correctAnswer']

    def get_options(self, obj):
        return [option.option_text for option in obj.options.all()]

    def get_correctAnswer(self, obj):
        correct_option = obj.options.filter(is_correct=True).first()
        return correct_option.option_text if correct_option else None


class QuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizSubmission
        fields = ['id', 'user', 'quiz', 'score', 'created_at', 'updated_at']
