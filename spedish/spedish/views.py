from django.contrib.auth import logout
from django.contrib.auth.models import User, Group

from rest_framework import viewsets
from rest_framework.response import Response

from spedish.serializers import NullSerializer, UserSerializer


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

    def list(self, request, format=None):
        """
        Returns whether the user is logged in or not

        Results is response status code
        """
        if request.user.is_authenticated():
            return Response(None, 200)
        else:
            return Response(None, 401)

    def destroy(self, request, format=None, pk=None):
        """
        Logout the current user, will accept any pk token for now

        Always return 200
        """
        logout(request)

        return Response(None, 200)
