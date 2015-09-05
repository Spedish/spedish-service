from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model): 
    """
    This model holds the user profile related to a particular user
    """
    # Each profile corresponds to exactly 1 users
    user = models.OneToOneField(User)
    
    isSeller = models.BooleanField()