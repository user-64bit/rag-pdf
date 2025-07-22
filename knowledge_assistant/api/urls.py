from django.urls import path
from .views import UploadDocumentView  
from .views import AskQuestionView  

urlpatterns = [
   # path('/', , name=''),
   path('upload/', UploadDocumentView.as_view(), name='upload-document'),
   path('ask-question/', AskQuestionView.as_view(), name='ask-question')
]