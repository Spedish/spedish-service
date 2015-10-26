from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailOnlyAuthBackend(ModelBackend):
    
    """
    Login the user session as long as the email address exists
    in the user database
    """
    
    def authenticate(self, email=None):
        try:
            return User.objects.get(email=email)
        except:
            return None
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None