"""
AI Chatbot Service using Google Gemini API for Grand Blue
Provides context-aware responses about water sports activities and booking information.
"""
import logging
from django.conf import settings
from merger.models import Activity

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class GrandBlueChatbotService:
    
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_API_KEY', None)
        self.model = None
        
        if not GENAI_AVAILABLE:
            logger.error("google-generativeai package not installed")
            return
            
        if self.api_key and self.api_key != 'YOUR_API_KEY_HERE':
            try:
                genai.configure(api_key=self.api_key)
                # Use the new Gemini 2.x models or fallback to 1.5
                model_attempts = [
                    'gemini-2.0-flash',           
                    'gemini-1.5-flash',
                    'gemini-pro',
                ]
                
                for model_name in model_attempts:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        # Test with a simple request
                        self.model.generate_content(
                            "Test",
                            generation_config={'max_output_tokens': 1}
                        )
                        logger.info(f"Successfully initialized model: {model_name}")
                        break
                    except Exception as e:
                        logger.debug(f"Model {model_name} not available: {e}")
                        continue
                
                if not self.model:
                    logger.error("Could not initialize any Gemini model")
            except Exception as e:
                logger.error(f"Error configuring Google AI: {e}")
                self.model = None
        else:
            logger.warning("Google API key not configured or is default placeholder")
    

    def _get_system_prompt(self):
        
        # Fetch all activities to provide up-to-date context
        activities = Activity.objects.all()
        activities_context = "AVAILABLE ACTIVITIES:\n"
        
        for activity in activities:
            activities_context += (
                f"- {activity.name} ({activity.activity_type}): "
                f"Rs {activity.base_price}/pax. "
                f"Location: {activity.location}. "
                f"Duration: {activity.duration}. "
                f"Max group: {activity.max_participants}. "
                f"Description: {activity.description[:100]}...\n"
            )
            
        system_prompt = f"""You are GrandBlueBot, the friendly and helpful AI assistant for 'Grand Blue', a premier water sports booking platform in Mauritius.

                            Your role is to assist users (both guests and logged-in members) with:
                            1. **Activity Information**: Providing details about our water sports (prices, duration, location, etc.).
                            2. **Booking Guidance**: Explaining how to book (select activity -> choose date/group size -> pay).
                            3. **General Inquiries**: Answering questions about Mauritius weather, safety, or location.

                            {activities_context}

                            **GUIDELINES:**
                            - **Tone**: Professional, welcoming, and enthusiastic about water sports. Use emojis occasionally (🌊 🚤 🐬).
                            - **Scope**: ONLY answer questions related to Grand Blue, water sports, and Mauritius tourism.
                            - **Limitations**: You CANNOT perform actions (like booking or cancelling) directly. You can only guide the user.
                            - **Privacy**: Do NOT ask for personal info like passwords or credit card details.
                            - **Unknowns**: If you don't know something (e.g., specific admin details), say "I recommend contacting our support team for that specific detail."

                            If a user asks about something unrelated (like coding, math, or politics), politely redirect them to Grand Blue activities.
                            """

        return system_prompt
    

    def get_response(self, user_message, conversation_history=None):

        if not self.model:
            return {
                'success': False,
                'response': "I'm currently offline. Please check that the Google API key is configured in settings.",
                'error': 'API key not configured'
            }
        
        try:
            # Build conversation context with dynamic system prompt
            prompt = self._get_system_prompt() + "\n\n"
            
            # Add conversation history (limit to last 5 messages to save tokens)
            if conversation_history:
                for msg in conversation_history[-5:]:
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    prompt += f"{role}: {msg['content']}\n\n"
            
            # Add current user message
            prompt += f"User: {user_message}\n\nAssistant:"
            
            # Call Google Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 300,
                }
            )
            
            return {
                'success': True,
                'response': response.text,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Google Gemini API error: {e}")
            return {
                'success': False,
                'response': "I'm having trouble connecting right now. Please try again in a moment.",
                'error': str(e)
            }

# Global service instance
_chatbot_service = None

def get_chatbot_service():
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = GrandBlueChatbotService()
    return _chatbot_service
