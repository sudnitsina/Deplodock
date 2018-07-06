# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse


class DashboardTest(TestCase):
    fixtures = ["tests/dashboard/user.json"]

    def test_index_redirect(self):
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertRedirects(response, '/login/?next=/dashboard/', status_code=302)

    def test_index_login(self):
        self.client.login(username='tester', password='tester123')
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/index.html')

