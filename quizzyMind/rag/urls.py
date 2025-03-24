from django.urls import path
from .views import *

urlpatterns = [
    path("upload-pdf/", UploadPDFView.as_view(), name="upload_pdf"),
    path("generate-quiz/", GenerateQuizView.as_view(), name="generate_quiz"),
]
