from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from api.models import Inventory
from authtoken.models import InventoryToken


class BaseTest(TestCase):
    fixtures = ["tests/api/test_inventory.json"]

    def test_token(self):
        self.client.force_login(User.objects.get_or_create(username='tester')[0])
        url = reverse('main')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'authtoken/token.html')
        self.assertContains(response, '790cb216be621e8b2e7c064e21f9f4fb020808071176655f9df1ac713f643d21')
        self.assertContains(response, 'ed6b741898abbcf2d4b0eb5dee0778d38a0b9f0b4af543e3b9c43710a44ee080')
        self.assertNotContains(response, 'ed6b741898abbcf2d4b0eb5dee0778d38a0b9f0b4af543e3b9c43710a44ee081')

    def test_scoped_token(self):
        self.client.force_login(User.objects.get_or_create(username='tester')[0])
        url = reverse('scoped')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'authtoken/scopedtoken.html')
        self.assertContains(response, 'test_inv')

    def test_create_token(self):
        self.client.force_login(User.objects.get_or_create(username='tester')[0])
        url = reverse('scoped')
        res = self.client.post(url, {'inventory': Inventory.objects.get(inventory="test_inv").pk, 'description': "token_description"})
        self.assertEquals(len(InventoryToken.objects.all()), 2)

    def test_delete_token(self):
        self.client.force_login(User.objects.get_or_create(username='tester')[0])
        url = reverse('scoped_delete', args=['ed6b741898abbcf2d4b0eb5dee0778d38a0b9f0b4af543e3b9c43710a44ee080'])
        res = self.client.get(url)
        self.assertEquals(len(InventoryToken.objects.all()), 0)