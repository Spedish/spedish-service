from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from spedish.serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class UserAuth(APIView):
    """
    This end point provides basic user authentication functionality
    """

    def post(self, request):
        """
        Login the indicated user
        ---
        response_serializer: UserSerializer
        parameters:
        - name: body
          pytype: UserSerializer
          paramType: body

        responseMessages:
            - code: 200
              message: Successfully logged in
            - code: 400
              message: Invalid request data
            - code: 401
              message: Login failed
        """
        try:
            inputSerializer = UserSerializer(data=request.data)
            
            if inputSerializer.is_valid():
                username = inputSerializer.data.get('username')
                password = inputSerializer.data.get('password')

                user = authenticate(username=username, password=password)
                if user is not None and user.is_active:
                    login(request, user)
                    return Response(None, status.HTTP_200_OK)
                
                return Response(None, status.HTTP_401_UNAUTHORIZED)
            
            else:
                return Response(None, status.HTTP_400_BAD_REQUEST)
        
        except:
            return Response(None, 401)

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
