from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from authentication.auth import CookieAuthentication
from rest_framework.permissions import IsAuthenticated

class StartQuizView(APIView):
    authentication_classes = [CookieAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        quiz_id = request.data.get("quiz_id")
        quiz = Quiz.objects.filter(id=quiz_id).first()

        if not quiz:
            return Response({"error": "No quiz found"}, status=status.HTTP_400_BAD_REQUEST)

        submission, created = QuizSubmission.objects.get_or_create(user=user, quiz=quiz)

        questions = quiz.questions.all()
        serialized_questions = QuestionSerializer(questions, many=True).data

        existing_answers = QuizSubmissionAnswer.objects.filter(submission=submission)
        answer_map = {answer.question.id: answer.selected_option.id for answer in existing_answers}

        for question in serialized_questions:
            question["selected_option"] = answer_map.get(question["id"], None)

        return Response({
            "submission_id": submission.id,
            "quiz_title": quiz.title,
            "questions": serialized_questions
        }, status=status.HTTP_200_OK)


class SubmitAnswerView(APIView):
    authentication_classes = [CookieAuthentication]
    permission_classes = [IsAuthenticated]

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
            selected_option=selected_option
        )

        submission.score = sum(1 for a in QuizSubmissionAnswer.objects.filter(submission=submission) if a.selected_option.is_correct)
        submission.save()

        return Response({"message": "Answer marked successfully"}, status=status.HTTP_200_OK)

class QuizResultView(APIView):
    authentication_classes = [CookieAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        quiz_id = request.data.get("quiz_id")
        user = request.user

        quizSubmission = QuizSubmission.objects.filter(user=user, quiz_id=quiz_id).first()
        if not quizSubmission:
            return Response({"error": "No submission found"}, status=status.HTTP_400_BAD_REQUEST)

        answers = QuizSubmissionAnswer.objects.filter(submission=quizSubmission)
        
        result_data = []
        for answer in answers:
            question = answer.question
            correct_option = question.options.filter(is_correct=True).first()
            result_data.append({
                "question": QuestionSerializer(question).data,
                "selected_option": OptionSerializer(answer.selected_option).data,
                "correct_option": OptionSerializer(correct_option).data if correct_option else None,
                "is_correct": answer.selected_option == correct_option
            })

        return Response({
            "quiz": quizSubmission.quiz.title,
            "total_questions": quizSubmission.quiz.questions.count(),
            "score": quizSubmission.score,
            "results": result_data
        }, status=status.HTTP_200_OK)



class ListAllQuizView(APIView):
    def get(self, request):
        quizzes = Quiz.objects.all()
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)
