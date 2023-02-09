"""swarm_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include

from rest_framework import routers
from swarm import views

# router = routers.DefaultRouter()
# router.register(r'sessions', views.SessionView, 'session')
# router.register(r'instagram_accounts', views.InstagramAccountView, 'instagram_account')
# router.register(r'medias', views.MediaView, 'media')

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/', include(router.urls)),
    path('api/scrape', views.scrape),
    path('api/scrape-dummy', views.scrape_dummy),
    # path('api/get_csrf', views.get_csrf)
]
