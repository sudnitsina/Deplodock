import binascii
import os

from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token as BaseToken

from api.models import Inventory


class Token(BaseToken):
    key = models.CharField('token', max_length=64, primary_key=True)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(32)).decode()


class InventoryToken(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    token = models.CharField('token', max_length=64, primary_key=True)
    inventory = models.ManyToManyField(Inventory)
    description = models.CharField(max_length=256, blank=False)
    created_date = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return '%s: %s' % (self.user, self.description)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(32)).decode()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_key()
        return super(InventoryToken, self).save(*args, **kwargs)
