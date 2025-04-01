from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from .auth import CookieAuthentication
from .models import Profile
from  api.models import *
from  api.serializers import *
from django.db.models import Max, Sum


class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Return tokens in the response body
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }

            return Response(
                {
                    "message": "User registered successfully",
                    "user": user_data,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        serializer = UserLoginSerializer(data=data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Return tokens in the response body
            return Response(
                {
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

class UserProfileDetailsView(APIView):
    authentication_classes = [CookieAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = UserSerializer(request.user).data
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile).data
        return Response({"user": user, "profile": serializer}, status=status.HTTP_200_OK)

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get best score per quiz (removes duplicate quiz attempts)
        best_submissions = (
            QuizSubmission.objects.filter(user=user)
            .values("quiz")
            .annotate(best_score=Max("score"))
        )

        if not best_submissions:
            return Response({
                "quizzes_taken": 0,
                "accuracy": "0%",
                "average_score": "0%",
                "highest_score": "0%"
            }, status=200)

        quizzes_taken = len(best_submissions)
        highest_score = max(sub["best_score"] for sub in best_submissions)
        average_score = sum(sub["best_score"] for sub in best_submissions) / quizzes_taken

        total_questions = sum(
            Question.objects.filter(quiz=sub["quiz"]).count() for sub in best_submissions
        )

        total_correct_answers = sum(sub["best_score"] for sub in best_submissions)

        accuracy = (total_correct_answers / total_questions) * 100 if total_questions else 0
        accuracy = min(accuracy, 100)  # Limit to 100%

        return Response({
            "quizzes_taken": quizzes_taken,
            "accuracy": f"{accuracy:.2f}%",
            "average_score": f"{average_score:.2f}%",
            "highest_score": highest_score
        }, status=200)
