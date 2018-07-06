from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import authentication
from rest_framework import exceptions

from .models import Token, InventoryToken
from api.models import Inventory


class ScopedTokenAuthentication(authentication.BaseAuthentication):
    """
    Simple token based authentication.
    Clients should authenticate by passing the token key in the "X-Auth-Token"
    HTTP header. For example:
    X-Auth-Token: a8a47e515bc04f5676d77bbd56eed54da8d57791fe1b225ace2c3cb62f82f03
    """
    def authenticate(self, request):
        if "HTTP_X_AUTH_TOKEN" not in request.META:
            return None
        if Token.objects.filter(key=request.META["HTTP_X_AUTH_TOKEN"]):
            user = get_object_or_404(
                User, auth_token__key=request.META["HTTP_X_AUTH_TOKEN"])
            return user, 'Full'
        elif InventoryToken.objects.filter(token=request.META["HTTP_X_AUTH_TOKEN"]):
            user = get_object_or_404(
                User, inventorytoken__token=request.META["HTTP_X_AUTH_TOKEN"])
            if not hasattr(request, 'inventory'):
                return user, 'Scoped: no inv'
            if not InventoryToken.objects.filter(
                    token=request.META["HTTP_X_AUTH_TOKEN"],
                    inventory=get_object_or_404(Inventory, user=user, inventory=request.inventory)):
                raise exceptions.AuthenticationFailed('Acess denied')
        else:
            raise exceptions.AuthenticationFailed('No such user')
        return user, 'Scoped'
