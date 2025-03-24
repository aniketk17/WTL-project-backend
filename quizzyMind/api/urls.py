from django.urls import path
from .views import *

urlpatterns = [
    path('get-all-quiz/', ListAllQuizView.as_view(), name='list_all_quiz_view'),
    path('start-quiz/', StartQuizView.as_view(), name='start_quiz_view'),
    path('submit-answer/', SubmitAnswerView.as_view(), name='submit_answer_view'),
    path('quiz-result/', QuizResultView.as_view(), name='quiz_result_view'),
]