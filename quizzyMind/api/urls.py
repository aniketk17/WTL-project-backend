from django.urls import path
from .views import *

urlpatterns = [
    path('quiz/', QuizListAPIView.as_view(), name='quiz-list'),
    path('quiz/<int:pk>/start/', StartQuizAPIView.as_view(), name='start-quiz'),
    path('quiz-submissions/', QuizSubmitAPIView.as_view(), name='quiz-submission-list'),
]
