from django.db import models
from django.contrib.auth.models import User
from localflavor.us.models import USStateField, USZipCodeField


class Address(models.Model):
    """
    This model holds the user address
    """
    line_one = models.CharField(max_length= 100)
    line_two = models.CharField(max_length = 100, blank=True)  # line_two is optional
    city = models.CharField(max_length = 50)
    state = USStateField()
    zip_code = USZipCodeField()


class UserProfile(models.Model):
    """
    This model holds the user profile related to a particular user
    """
    # Each profile corresponds to exactly 1 users
    user = models.OneToOneField(User)
    isSeller = models.BooleanField()
    address = models.OneToOneField(Address, default = '')



