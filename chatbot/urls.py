from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat, name='chat'),
    path('documents/', views.document_list, name='document_list'),
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('documents/delete/<int:pk>/', views.delete_document, name='delete_document'),
    path('clear-chat/', views.clear_chat, name='clear_chat'),
]