import uuid
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import ChatConversation, ChatMessage
from .ai_service import get_chatbot_service

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
def chat_message(request):
    """
    Handle chat messages via AJAX
    """
    try:
        user_message = request.POST.get('message', '').strip()
        session_id = request.POST.get('session_id', '')
        
        if not user_message:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'})
        
        # Generate session ID if missing
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get or create conversation
        conversation, created = ChatConversation.objects.get_or_create(
            session_id=session_id,
            defaults={'user': request.user if request.user.is_authenticated else None}
        )
        
        # Update user if they logged in since starting chat
        if request.user.is_authenticated and not conversation.user:
            conversation.user = request.user
            conversation.save()
        
        # Save user message
        ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        # Get conversation history
        messages = list(conversation.messages.all())
        conversation_history = [
            {'role': msg.role, 'content': msg.content}
            for msg in (messages[:-1] if len(messages) > 1 else [])
        ]
        
        # Get AI response
        chatbot = get_chatbot_service()
        result = chatbot.get_response(user_message, conversation_history)
        
        if result['success']:
            # Save AI response
            ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=result['response']
            )
            
            return JsonResponse({
                'success': True,
                'response': result['response'],
                'session_id': session_id
            })
        else:
            return JsonResponse({
                'success': True, # Return true to show fallback message in UI
                'response': result['response'], # Error message from service
                'error': result.get('error')
            })
            
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e),
            'response': "Sorry, something went wrong. Please try again."
        })

def chat_history(request):
    """Get chat history for current session"""
    session_id = request.GET.get('session_id', '')
    
    if not session_id:
        return JsonResponse({'success': False, 'messages': []})
    
    try:
        conversation = ChatConversation.objects.get(session_id=session_id)
        messages = conversation.messages.all().values('role', 'content', 'created_at')
        
        return JsonResponse({
            'success': True,
            'messages': list(messages)
        })
    except ChatConversation.DoesNotExist:
        return JsonResponse({'success': False, 'messages': []})
