# -*- coding: utf-8 -*- #
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^scopedtoken$', views.scoped, name='scoped'),
    url(r'^scopedtoken/([A-z0-9-_.:]+)$', views.scoped_edit,
        name='scoped_edit'),
    url(r'^scopedtoken/delete/([A-z0-9-_.:]+)$', views.scoped_delete,
        name='scoped_delete'),
    url(r'^token/delete/([A-z0-9-_.:]+)$', views.token_delete,
        name='token_delete'),
]
