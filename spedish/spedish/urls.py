"""spedish URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers
router = routers.DefaultRouter()

from spedish import views


urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),                                 # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),                                      # django admin web portal
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')), # Rest framework internal URLs
    url(r'^docs/', include('rest_framework_swagger.urls')),                         # Swagger
    
    # API end points
    url(r'^', include(router.urls)),                                    # Hook up the endpoints from the router
    url(r'^auth/$', views.UserAuth.as_view(), name='user-auth-api'),
    url(r'^user-profile/$', views.UserProfileMgr.as_view(), name='user-profile-api'),
    url(r'^product-profile/$', views.ProductProfileMgr.as_view(), name='product-profile-api'),
]
