from rest_framework.authtoken.views import ObtainAuthToken

class LoginForToken(ObtainAuthToken):
    authentication_classes = [ ]

