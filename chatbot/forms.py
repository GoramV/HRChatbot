from django import forms
from .models import Document, ChatMessage

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['file'].widget.attrs.update({'class': 'form-control'})
        
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            file_extension = file.name.split('.')[-1].lower()
            if file_extension == 'pdf':
                self.instance.document_type = 'pdf'
            elif file_extension == 'txt':
                self.instance.document_type = 'txt'
            else:
                raise forms.ValidationError("Only PDF and TXT files are allowed.")
        return file

class ChatForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['content']
        labels = {'content': ''}
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ask a question about HR policies...',
                'autofocus': True
            })
        }