"""wcmd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include, re_path
from wcmd.wcmd.views import *

urlpatterns = [
    path('wcmd/admin/', admin.site.urls),
    re_path(r'^wcmd/accounts/$', user_landing, name='user_landing'),
    path('wcmd/accounts/', include('allauth.urls')),
    path('wcmd/accounts/user/', UserList.as_view(), name='user_list'),
    path('wcmd/accounts/user/<str:username>', user_detail, name='user_detail'),
    #path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('wcmd/', include('wcmd.wcmd.urls'))
]
