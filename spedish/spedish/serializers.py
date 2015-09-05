import copy

from django.contrib.auth.models import User
from rest_framework import serializers

from spedish.models import UserProfile
from django.db import transaction


class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        
        
class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        
        
class UserWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')
        

class UserProfileReadSerializer(serializers.ModelSerializer):
    user = UserReadSerializer(many = False, read_only = True)
    
    class Meta:
        model = UserProfile
        fields = ('user', 'isSeller')

        
class UserProfileWriteSerializer(serializers.ModelSerializer):
    user = UserWriteSerializer(many = False, read_only = False)

    class Meta:
        model = UserProfile
        fields = ('user', 'isSeller')
        
    @transaction.atomic
    def create(self, validated_data):
        data = copy.deepcopy(validated_data)
        userData = data.pop('user')
        
        userRec =  User(**userData)
        userRec.set_password(userData.get('password'))
        userRec.save()
        
        userProfileRec = UserProfile(user = userRec, **data)
        userProfileRec.save()
        
        return userProfileRec