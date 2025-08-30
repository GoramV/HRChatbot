from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Document(models.Model):
    DOCUMENT_TYPES = (
        ('pdf', 'PDF'),
        ('txt', 'Text'),
    )
    
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    document_type = models.CharField(max_length=3, choices=DOCUMENT_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Session {self.id} - {self.user.username}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = (
        ('user', 'User'),
        ('bot', 'Bot'),
    )
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=4, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."
