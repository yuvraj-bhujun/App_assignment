from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    """
    
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        if email is None:
            email = username
            
        if email is None or password is None:
            return None
            
        try:
            user = User.objects.get(Q(email=email))
        except User.DoesNotExist:
            User().set_password(password)
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None