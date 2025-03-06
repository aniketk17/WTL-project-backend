import jwt
from django.conf import settings
from .models import User
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken

class CookieAuthentication(BaseAuthentication):
   
    def authenticate(self, request):
        token = request.COOKIES.get("access_token")

        if not token:
            return None

        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = User.objects.get(id=user_id)
            return (user, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed(_("Token has expired."))
        except jwt.DecodeError:
            raise AuthenticationFailed(_("Invalid token."))
        except User.DoesNotExist:
            raise AuthenticationFailed(_("User not found."))

        return None
