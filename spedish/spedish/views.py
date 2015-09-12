from django.contrib.auth import logout, authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from spedish.models import UserProfile
from spedish.serializers import UserProfileWriteSerializer, \
    UserProfileReadSerializer, UserProfileUpdateSerializer


class UserProfileMgr(APIView):
    """
    User profile management
    """

    def post(self, request):
        """
        Create new user profile
        ---
        parameters:
        - name: profileData
          pytype: UserProfileWriteSerializer
          paramType: body

        responseMessages:
            - code: 201
              message: Successfully created
            - code: 400
              message: Invalid request data
        """
        try:
            inputSerializer = UserProfileWriteSerializer(data = request.data)
            if inputSerializer.is_valid(raise_exception = True):
                inputSerializer.save()
                return Response(None, status.HTTP_201_CREATED)

        except:
            return Response(None, status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Update a user profile, username, password and seller status cannot be updated here
        
        To insert an address, set id to 0
        ---
        parameters:
        - name: username
          description: which user to update
          type: string
          paramType: query
          required: true
        - name: profileData
          pytype: UserProfileUpdateSerializer
          paramType: body

        responseMessages:
            - code: 200
              message: Successfully updated
            - code: 400
              message: Invalid request data
        """
        try:
            user = UserProfile.objects.get(user__username=request.GET['username'])

            inputSerializer = UserProfileUpdateSerializer(instance=user, data = request.data)
            if inputSerializer.is_valid(raise_exception = True):
                inputSerializer.save()
                return Response(None, status.HTTP_200_OK)

        except:
            return Response(None, status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        Get user profile(s)
        ---
        response_serializer: UserProfileReadSerializer
        parameters:
        - name: username
          description: retrieve profile for a single user
          type: string
          paramType: query
          required: true

        responseMessages:
            - code: 200
              message: Successfully created
            - code: 400
              message: Invalid request data
            - code: 404
              message: User not found
        """
        try:
            # use the profile serializer to get the username
            username = request.GET['username']

            try:
                profile = UserProfile.objects.get(user__username = username)

                return Response(UserProfileReadSerializer(profile).data, status.HTTP_200_OK)

            except ObjectDoesNotExist:
                return Response(None, status.HTTP_404_NOT_FOUND)

        except:
            return Response(None, status.HTTP_400_BAD_REQUEST)


class UserAuth(APIView):
    """
    Basic user authentication functionality
    """

    def post(self, request):
        """
        Login the indicated user
        ---
        parameters:
        - name: username
          paramType: form
          required: true
        - name: password
          paramType: form
          required: true

        responseMessages:
            - code: 200
              message: Successfully logged in
            - code: 400
              message: Invalid request data
            - code: 401
              message: Login failed
        """
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(username = username, password = password)
            if user is not None and user.is_active:
                login(request, user)
                return Response(None, status.HTTP_200_OK)

            return Response(None, status.HTTP_401_UNAUTHORIZED)

        except:
            return Response(None, status.HTTP_400_BAD_REQUEST)

    def get(self, request):

        """
        Check if the requester is logged in
        ---
        responseMessages:
            - code: 200
              message: User is logged in
            - code: 401
              message: User is not logged in
        """
        if request.user.is_authenticated():
            return Response(None, 200)
        else:
            return Response(None, 401)

    def delete(self, request):
        """
        Logout the current user
        ---
        responseMessages:
            - code: 200
              message: Always returns this status
        """
        logout(request)
        return Response(None, 200)
