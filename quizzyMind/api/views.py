from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import *
from .serializers import *

class QuizListAPIView(APIView):
    """Handles retrieving all quizzes and creating a new quiz"""
    
    def get(self, request):
        quizzes = Quiz.objects.all()
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StartQuizAPIView(APIView):
    """Handles starting a quiz for an authenticated user"""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        quiz = get_object_or_404(Quiz, pk=pk)

        questions = quiz.questions.all()

        serialized_questions = [
            {
                "id": question.id,
                "text": question.text,
                "options": [
                    {
                        "option_id": option.id,
                        "option_text": option.option_text,
                        "correct": option.is_correct
                    }
                    for option in question.options.all()
                ],
            }
            for question in questions
        ]

        return Response({"questions": serialized_questions}, status=status.HTTP_200_OK)


class QuizSubmitAPIView(APIView):
    """Handles submitting a quiz and calculating the score"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        quiz_id = request.data.get("quiz_id")
        answers = request.data.get("answers")

        quiz = get_object_or_404(Quiz, pk=quiz_id)
        submission = QuizSubmission.objects.create(user=user, quiz=quiz)

        total_score = 0
        submitted_answers = []

        for answer in answers:
            question_id = answer.get("question_id")
            selected_option_id = answer.get("selected_option_id")

            question = get_object_or_404(Question, pk=question_id)
            selected_option = get_object_or_404(Option, pk=selected_option_id)

            is_correct = selected_option.is_correct
            if is_correct:
                total_score += 1

            submitted_answers.append({
                "question": {
                    "text": question.text,
                    "options": [option.option_text for option in question.options.all()],
                    "correctAnswer": question.options.filter(is_correct=True).first().option_text
                },
                "selected_option": selected_option.option_text
            })

        submission.score = total_score
        submission.save()

        return Response({
            "submission": QuizSubmissionSerializer(submission).data,
            "message": "Quiz submitted successfully",
            "total_score": total_score,
            "submitted_answers": submitted_answers
        }, status=status.HTTP_200_OK)
