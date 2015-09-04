from django.contrib.auth import logout
from django.contrib.auth.models import User, Group

from rest_framework import viewsets
from rest_framework.response import Response

from spedish.serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class UserAuth(viewsets.ViewSet):
    """
    This end point provides basic user control
    """

    # We are not expecting to query a model and we do not need
    # to return data (only status code)
    queryset = User.objects.none()
    serializer_class = UserSerializer

    def create(self, request, format=None, pk=None):
        """
        Login the indicated user
        ---
        response_serializer: UserSerializer
        parameters:
        - name: body
          pytype: UserSerializer
          paramType: body
        - name: idInPath
          paramType: path
        - name: idInForm
          pytype: UserSerializer
          paramType: form
        responseMessages:
            - code: 200
              message: Successfully logged in
            - code: 401
              message: Login failed
        """
        try:
            inputSerializer = UserSerializer(data=request.DATA)
            username = inputSerializer.data['username']
            password = inputSerializer.data['password']

            return Response(None, 200)
        except Exception as e:
            return Response(None, 401)


    def list(self, request, format=None):
        """
        Returns whether the user is logged in or not
        ---
        responseMessages:
            - code: 200
              message: User currently logged in
            - code: 403
              message: User currently not logged in
        """
        model = User
        request_serializer = UserSerializer
        serializer_class = UserSerializer
        if request.user.is_authenticated():
            return Response(None, 200)
        else:
            return Response(None, 401)

    def destroy(self, request, format=None, pk=None):
        """
        Logout the current user, will accept any pk token for now
        ---
        responseMessages:
            - code: 200
              message: Always returns this status
        """
        request_serializer = UserSerializer
        serializer_class = UserSerializer

        #logout(request)

        return Response(None, 200)
