from rest_framework import generics, status
from rest_framework.response import Response
from .models import UploadedDocument
from .serializers import UploadedDocumentSerializer
from .utils import extract_text, chunk_text, store_in_chromadb, retrieve_relevant_chunks, build_prompt
import os
from rest_framework.views import APIView

from rest_framework.parsers import MultiPartParser
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import UploadedDocument
from .serializers import UploadedDocumentSerializer
from .utils import extract_text, chunk_text, store_in_chromadb
import openai

class UploadDocumentView(generics.GenericAPIView):
    queryset = UploadedDocument.objects.all()
    serializer_class = UploadedDocumentSerializer
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('file')
        if not files:
            return Response({"error": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)

        responses = []

        for f in files:
            serializer = self.get_serializer(data={"file": f})
            if serializer.is_valid():
                instance = serializer.save()
                try:
                    file_path = instance.file.path
                    filename = os.path.basename(file_path)
                    text = extract_text(file_path)
                    chunks = chunk_text(text)
                    store_in_chromadb(chunks, filename, document_id=str(instance.id))
                    instance.processed = True
                    instance.save()
                    responses.append(UploadedDocumentSerializer(instance).data)
                except Exception as e:
                    responses.append({
                        "file": f.name,
                        "error": str(e)
                    })
            else:
                responses.append({
                    "file": f.name,
                    "error": serializer.errors
                })

        return Response(responses, status=status.HTTP_201_CREATED)




class AskQuestionView(APIView):
    def post(self, request):
        
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        question = request.data.get("question", "").strip()
        if not question:
            return Response({"error": "Question is required."}, status=400)

        try:
            chunks, metadatas = retrieve_relevant_chunks(question)
            prompt = build_prompt(chunks, question)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=500
            )

            answer = response.choices[0].message.content.strip()
            sources = list({f"{m['source']} - Page {m['page']}" for m in metadatas})

            return Response({
                "answer": answer,
                "sources": sources
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)