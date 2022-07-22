"""JourneyGo URL Configuration

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
from unicodedata import name
from django.contrib import admin
from django.urls import path
from jg_app import views
from django.conf.urls import include

urlpatterns = [
    path('',include('jg_app.urls')),
    path('index/', views.index, name='index'),
    path('admin/', admin.site.urls, name='admin'),
    path('result/', views.result, name='result'),
    path('friends/', views.friends, name='friends'),
    path('searchPage/', views.searchRec, name='searchPage'),
    path('start/', views.startDropDown, name='start'),
    path('setting/', views.setting, name='setting'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('room2/', views.room2, name='room2'),
    path('confirmPage/', views.confirmPage, name='confirmPage'),
    path('spotvote/', views.spotvote, name='spotvote'),
    path('ready/', views.ready, name='ready'),
    path('decide/', views.decide, name='decide')
]
