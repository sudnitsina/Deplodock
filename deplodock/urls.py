"""inventory URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import login, logout,  PasswordResetView, \
    PasswordResetCompleteView, PasswordResetConfirmView, password_reset_done
from django.views.generic.base import TemplateView

handler404 = 'api.views.not_found'

urlpatterns = [
    url(r'^$', include('authtoken.urls'), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^accounts/profile/', include('authtoken.urls'), name='home'),
    # url(r'^registration/', include('registration.urls')),
    url(r'^login/$', login, {'template_name': 'dashboard/login.html'},
        name='login'),
    url(r'^logout/$', logout, {'template_name': 'dashboard/logout.html'},
        name='logout'),
    # url(r'^auth/', include('social_django.urls', namespace='social')),
    # url(r'^password_reset/$',
    #     PasswordResetView.as_view(template_name='password/password_reset_form.html',
    #                               email_template_name='password/password_reset_email.html',
    #                               subject_template_name='password/password_reset_subject.txt',),
    #     name='password_reset'),
    # url(r'^password_reset/done/$', password_reset_done, {'template_name': 'password/password_reset_done.html'},
    #     name='password_reset_done'),
    # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #     PasswordResetConfirmView.as_view(template_name='password/password_reset_confirm.html'),
    #     name='password_reset_confirm'),
    # url(r'^reset/done/$',
    #     PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'),
    #     name='password_reset_complete'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
