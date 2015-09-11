import copy

from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers

from spedish.models import UserProfile, Address


class UserAddressReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'line_one', 'line_two', 'city', 'state', 'zip_code')


class UserAddressWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('line_one', 'line_two', 'city', 'state', 'zip_code')


class UserAddressUpdateSerializer(serializers.ModelSerializer):
    address_id = serializers.IntegerField()

    class Meta:
        model = Address
        fields = ('address_id', 'line_one', 'line_two', 'city', 'state', 'zip_code')


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


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class UserProfileReadSerializer(serializers.ModelSerializer):
    user = UserReadSerializer(many = False, read_only = True)
    address = UserAddressReadSerializer(many = True, read_only = True)

    class Meta:
        model = UserProfile
        fields = ('user', 'isSeller', 'address')


class UserProfileWriteSerializer(serializers.ModelSerializer):
    user = UserWriteSerializer(many = False, read_only = False)
    address = UserAddressWriteSerializer(many = True, read_only = False)

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
            # id field in data is used for looking up address only
            if 'id' in item:
                del item['id']
            userAddress = Address(user = userProfileRec, **item)
            userAddress.save()

        return userProfileRec


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer(many = False, read_only = False)
    address = UserAddressUpdateSerializer(many = True, read_only = False)

    class Meta:
        model = UserProfile
        fields = ('user', 'address')

    @transaction.atomic
    def update(self, instance, validated_data):
        # UserProfile is made up of User, UserProfile and Address, we unpack
        # the data for each first
        data = copy.deepcopy(validated_data)
        userData = data.pop('user')
        addrList = data.pop('address')

        # Update User
        userRec = instance.user
        self._setFields(userRec, userData, [])
        userRec.save()

        # Update the address list
        updatedIds = set()
        for addr in addrList:
            try:
                addrRec = instance.address.get(id=addr.get('address_id'))
                self._setFields(addrRec, addr, [])
                addrRec.save()
            except ObjectDoesNotExist:
                # insert a new address if the entry currently does not exist
                del addr['address_id']
                addrRec = Address(user=instance, **addr)
                addrRec.save()
            finally:
                # Keep track of which IDs we operated on, these are the active
                # IDs that we either updated or added
                updatedIds.add(addrRec.id)

        # Delete entries that are no longer present
        allIds = set([record.id for record in instance.address.all()])
        for deleteId in allIds.difference(updatedIds):
            addrRec = instance.address.get(id=deleteId)
            addrRec.delete()

        # Update UserProfile
        # TODO: There are no other fields so nothing is written
        return instance

    def _setFields(self, instance, data, ignoreField):
        for attr, val in data.items():
            if attr not in ignoreField:
                setattr(instance, attr, val)


