from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

class StartQuizView(APIView):
    def post(self, request, quiz_id):
        user = request.user
        quiz = Quiz.objects.filter(id=quiz_id)

        if not quiz:
            return Response({"error": "No quiz Found"}, status=status.HTTP_400_BAD_REQUEST)

        submission = QuizSubmission.objects.create(user=user, quiz=quiz)
        first_question = quiz.questions.first()

        if not first_question:
            return Response({"error": "No questions available"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "submission_id": submission.id,
            "question": QuestionSerializer(first_question).data,
            "selected_option": None
        }, status=status.HTTP_200_OK)

class SubmitAnswerView(APIView):
    def post(self, request):
        submission_id = request.data.get("submission_id")
        question_id = request.data.get("question_id")
        selected_option_id = request.data.get("selected_option_id")

        try:
            submission = QuizSubmission.objects.get(id=submission_id)
            question = Question.objects.get(id=question_id)
            selected_option = Option.objects.get(id=selected_option_id)
        except (QuizSubmission.DoesNotExist, Question.DoesNotExist, Option.DoesNotExist):
            return Response({"error": "Invalid submission, question, or option"}, status=status.HTTP_400_BAD_REQUEST)

        answer, created = QuizSubmissionAnswer.objects.update_or_create(
            submission=submission,
            question=question,
            defaults={"selected_option": selected_option}
        )

        if selected_option.is_correct:
            submission.score += 1
            submission.save()

        next_question = submission.quiz.questions.filter(question_number__gt=question.question_number).first()

        if not next_question:
            return Response({
                "message": "Quiz Completed!",
                "score": submission.score,
                "total_questions": submission.quiz.questions.count()
            }, status=status.HTTP_200_OK)

        return Response({
            "question": QuestionSerializer(next_question).data,
            "selected_option": None
        }, status=status.HTTP_200_OK)

class NavigateView(APIView):
    def post(self, request):
        submission_id = request.data.get("submission_id")
        question_id = request.data.get("question_id")
        direction = request.data.get("direction")  # 'previous' or 'next'

        if direction not in ["previous", "next"]:
            return Response({"error": "Invalid direction"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            submission = QuizSubmission.objects.get(id=submission_id)
            current_question = Question.objects.get(id=question_id)
        except (QuizSubmission.DoesNotExist, Question.DoesNotExist):
            return Response({"error": "Invalid submission or question"}, status=status.HTTP_400_BAD_REQUEST)

        if direction == "previous":
            target_question = submission.quiz.questions.filter(question_number__lt=current_question.question_number).last()
        else:
            target_question = submission.quiz.questions.filter(question_number__gt=current_question.question_number).first()

        if not target_question:
            return Response({"error": f"No {direction} question available"}, status=status.HTTP_400_BAD_REQUEST)

        existing_answer = QuizSubmissionAnswer.objects.filter(submission=submission, question=target_question).first()

        return Response({
            "question": QuestionSerializer(target_question).data,
            "selected_option": existing_answer.selected_option.id if existing_answer else None
        }, status=status.HTTP_200_OK)
