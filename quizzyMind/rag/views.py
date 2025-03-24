from django.core.files.storage import default_storage
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
import os
from .utils import generate_quiz
import uuid

class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        pdf_file = request.FILES.get('pdf')
        if not pdf_file:
            return Response({"error": "No PDF file provided"}, status=400)

        if not pdf_file.name.lower().endswith(".pdf"):
            return Response({"error": "Only PDF files are allowed."}, status=400)

        # Define the upload directory as rag/uploads
        upload_dir = os.path.join(settings.MEDIA_ROOT, "rag", "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # Generate a unique filename to avoid collisions
        unique_filename = f"{uuid.uuid4().hex}_{pdf_file.name}"
        file_path = os.path.join(upload_dir, unique_filename)

        # Save the file
        with open(file_path, "wb+") as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        return Response({"message": "PDF uploaded successfully!", "file_path": file_path})


class GenerateQuizView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt", "")
        file_path = request.data.get("file_path", "")

        if not prompt:
            return Response({"error": "Prompt is required"}, status=400)
        if not file_path:
            return Response({"error": "File path is required"}, status=400)

        if not os.path.exists(file_path):
            return Response({"error": "File not found"}, status=404)

        try:
            quiz = generate_quiz(prompt, file_path)  # Pass the file_path to generate_quiz
            return Response({"prompt": prompt, "quiz": quiz})
        except Exception as e:
            return Response({"error": str(e)}, status=500)