from django.contrib import admin
from .models import Document, ChatSession, ChatMessage

# Register your models here.
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'uploaded_at', 'uploaded_by')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('title',)

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    list_filter = ('created_at',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('message_type', 'content', 'timestamp', 'session')
    list_filter = ('message_type', 'timestamp')
