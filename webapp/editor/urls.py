from django.conf.urls import url
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('control/', views.control),
    url(r'^$', views.index),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup', views.signup, name='signup'),
    path('accounts/activate/<int:uid>/<slug:token>', views.activate, name='activate'),
    path('accounts/resend_activation', views.resend_activation_link, name='resend_activation')
]
