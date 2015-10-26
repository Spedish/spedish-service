from django.contrib.auth import logout, authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

import facebook

from spedish.models import UserProfile
from spedish.serializers import UserProfileWriteSerializer, \
    UserProfileReadSerializer, UserProfileUpdateSerializer
from facebook import GraphAPIError
    

class SessionCsrfExemptAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class UserProfileMgr(APIView):
    """
    User profile management
    """

    # This endpoint requires a valid user
    authentication_classes = ([SessionCsrfExemptAuthentication])
    permission_classes = ([IsAuthenticated])

    def get_permissions(self):
        # allow non-authenticated user to create via POST
        return ([AllowAny()] if self.request.method == 'POST'
            else [IsAuthenticated()])

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
            # At this point the rest endpoint ensure we are logged in
            user = UserProfile.objects.get(user__username=request.user.username)

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
            # Use the profile serializer to get the username
            # Endpoint guarantees there is a logged in user
            profile = UserProfile.objects.get(user__username = request.user.username)

            return Response(UserProfileReadSerializer(profile).data, status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(None, status.HTTP_404_NOT_FOUND)
        except:
            return Response(None, status.HTTP_400_BAD_REQUEST)


class FBUserAuth(APIView):
    """
    Handles user authentication through FB, only the FB login process is different
    other operations can still be performed on the normal UserAuth interface
    after the user has been logged in
    """
    
    authentication_classes = ([SessionCsrfExemptAuthentication])
    
    def post(self, request):
        """
        Login the indicated user using a FB access token
        ---
        parameters:
        - name: access_token
          paramType: form
          required: true
          
        responseMessages:
        - code: 200
          message: Successfully logged in
        - code: 400
          message: Invalid request data
        - code: 401
          message: Login failed
        - code: 404
          messaage: Token is valid however user does not exist in Spedish database
        """
        
        try:
            token = request.POST.get('token')
            
            """
            For testing purposes get a test token from http://www.spedish.com/fb.html
            and uncomment the line below
            
            If the below operation fails using the token, you may need to renew it
            (by default the token is only valid for ~1hr
            """ 
            token = 'CAAXoqw6AxAwBAGGKJDozo9LM52qnQKWUkCQWZAc2n2S32gT4WHD3NhKBVuHZBl8pzk0aBsPIznkw2X0u9i9Iv6Ppx0T0wwHpesSHwQOK3X6cT7CRFKXJGwFs7SVXcY6xlmFChEEDNuorngpf8aqpEuaWIrKXmrbmhfjCrKOfmQbjajYthScYwZABJV7Fkr8MxfhZA8AzF8pQ29HrAZBFO'            
            
            # Ask FB for user email
            fb = facebook.GraphAPI(token)
            me = fb.get_object("me", fields='id,name,email')
            
            #me = fb.get('me', fields="id,name,email")
            if not me['email']:
                return Response(None, status.HTTP_400_BAD_REQUEST)
            
            # Get Spedish user through the email address
            profile = UserProfile.objects.get(user__email = me['email']) 
            if not profile:
                return Response(None, status.HTTP_404_NOT_FOUND)
            
            # Login the user
            user = authenticate(email=profile.user.email)
            login(request, user)
            return Response(None, status.HTTP_200_OK)
            
        except GraphAPIError as e:
            # catch the invalid login case and return a generic error for the rest 
            if e.result['error']['code'] == 190:
                return Response(None, status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(None, status.HTTP_400_BAD_REQUEST)
                
        except:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        

class UserAuth(APIView):
    """
    User authentication functionality
    """

    authentication_classes = ([SessionCsrfExemptAuthentication])

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
