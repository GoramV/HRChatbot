from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction
from .models import Document, ChatSession, ChatMessage
from .forms import DocumentForm, ChatForm
from .rag_utils import RAGProcessor

# Helper function to check if user is admin
def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
def home(request):
    """Home view for the chatbot"""
    # Get or create a chat session for the user
    chat_session, created = ChatSession.objects.get_or_create(
        user=request.user,
        defaults={'user': request.user}
    )
    
    # Get chat history
    chat_history = ChatMessage.objects.filter(session=chat_session).order_by('timestamp')
    
    # Chat form
    chat_form = ChatForm()
    
    return render(request, 'chatbot/home.html', {
        'chat_session': chat_session,
        'chat_history': chat_history,
        'chat_form': chat_form,
    })

@login_required
@require_POST
def chat(request):
    """Process chat messages"""
    # Get the current chat session
    chat_session = ChatSession.objects.get(user=request.user)
    
    # Process the form
    form = ChatForm(request.POST)
    if form.is_valid():
        # Save the user message
        user_message = form.save(commit=False)
        user_message.session = chat_session
        user_message.message_type = 'user'
        user_message.save()
        
        # Process the message with RAG
        try:
            # Initialize RAG processor
            rag = RAGProcessor()
            
            # Get all documents
            documents = Document.objects.all()
            
            # Check if there are any documents
            if not documents.exists():
                answer = "I'm sorry, there are no HR policy documents uploaded yet. Please contact an administrator to upload the necessary documents."
            else:
                # Process documents and create vector store
                vector_store = rag.process_documents(documents)
                
                # Get answer
                answer = rag.get_answer(vector_store, user_message.content)
            
            # Save the bot response
            bot_message = ChatMessage.objects.create(
                session=chat_session,
                message_type='bot',
                content=answer
            )
            
            # Return both messages for AJAX response
            return JsonResponse({
                'status': 'success',
                'user_message': {
                    'content': user_message.content,
                    'timestamp': user_message.timestamp.strftime('%H:%M')
                },
                'bot_message': {
                    'content': bot_message.content,
                    'timestamp': bot_message.timestamp.strftime('%H:%M')
                }
            })
            
        except Exception as e:
            # Log the error
            print(f"Error processing message: {str(e)}")
            
            # Save a generic error message
            bot_message = ChatMessage.objects.create(
                session=chat_session,
                message_type='bot',
                content="I'm sorry, I encountered an error processing your request."
            )
            
            return JsonResponse({
                'status': 'error',
                'user_message': {
                    'content': user_message.content,
                    'timestamp': user_message.timestamp.strftime('%H:%M')
                },
                'bot_message': {
                    'content': bot_message.content,
                    'timestamp': bot_message.timestamp.strftime('%H:%M')
                }
            })
    
    return JsonResponse({'status': 'error', 'errors': form.errors})

@login_required
@user_passes_test(is_admin)
def document_list(request):
    """List all documents (admin only)"""
    documents = Document.objects.all().order_by('-uploaded_at')
    return render(request, 'chatbot/document_list.html', {'documents': documents})

@login_required
@user_passes_test(is_admin)
def upload_document(request):
    """Upload a new document (admin only)"""
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            return redirect('document_list')
    else:
        form = DocumentForm()
    
    return render(request, 'chatbot/upload_document.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_document(request, pk):
    """Delete a document (admin only)"""
    document = Document.objects.get(pk=pk)
    if request.method == 'POST':
        document.delete()
        return redirect('document_list')
    
    return render(request, 'chatbot/delete_document.html', {'document': document})

@login_required
def clear_chat(request):
    """Clear the chat history for the current session"""
    if request.method == 'POST':
        chat_session = ChatSession.objects.get(user=request.user)
        ChatMessage.objects.filter(session=chat_session).delete()
        return redirect('home')
    
    return redirect('home')
