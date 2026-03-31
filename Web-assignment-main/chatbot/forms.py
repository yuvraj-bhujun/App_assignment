from django import forms
from .models import ChatMessage, ChatConversation


class ChatMessageModelForm(forms.ModelForm):
    """
    ModelForm for ChatMessage - allows creating/editing chat messages
    Can be used for admin moderation or message management
    """
    class Meta:
        model = ChatMessage
        fields = ['conversation', 'role', 'content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Enter message content...'
            }),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'conversation': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'conversation': 'Chat Conversation',
            'role': 'Message Role',
            'content': 'Message Content'
        }
    
    def clean_content(self):
        """Ensure message content is not empty"""
        content = self.cleaned_data.get('content')
        if content and len(content.strip()) < 1:
            raise forms.ValidationError('Message content cannot be empty.')
        return content


class ChatConversationModelForm(forms.ModelForm):
    """
    ModelForm for ChatConversation - manage chat sessions
    """
    class Meta:
        model = ChatConversation
        fields = ['user', 'session_id']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'session_id': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
        }
        labels = {
            'user': 'User',
            'session_id': 'Session ID'
        }
