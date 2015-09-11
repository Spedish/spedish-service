import copy

from django.contrib.auth.models import User
from rest_framework import serializers

from spedish.models import UserProfile, Address
from django.db import transaction


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'line_one', 'line_two', 'city', 'state', 'zip_code')


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
    address = UserAddressSerializer(many = True, read_only = True)

    class Meta:
        model = UserProfile
        fields = ('user', 'isSeller', 'address')


class UserProfileWriteSerializer(serializers.ModelSerializer):
    user = UserWriteSerializer(many = False, read_only = False)
    address = UserAddressSerializer(many = True, read_only = False)

    class Meta:
        model = UserProfile
        fields = ('user', 'isSeller', 'address')
        
    @transaction.atomic
    def create(self, validated_data):
        data = copy.deepcopy(validated_data)
        userData = data.pop('user')
        address = data.pop('address')

        userRec =  User(**userData)
        userRec.set_password(userData.get('password'))
        userRec.save()

        userProfileRec = UserProfile(user = userRec, **data)
        userProfileRec.save()

        for item in address:
            userAddress = Address(user = userProfileRec, **item)
            userAddress.save()
        
        return userProfileRec



