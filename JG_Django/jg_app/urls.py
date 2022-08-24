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

from django.urls import path
from jg_app import views


urlpatterns = [
    path('',views.index,name='index'),
    path('',views.friends,name='friends'),
    path('',views.searchRec,name='searchRec'),
    path('',views.startDropDown,name='startDropDown'),
    path('',views.setting,name='setting'),
    path('',views.room,name='room'),
    path('',views.room2,name='room2'),
    path('',views.spotvote,name='spotvote'),
    path('',views.ready,name='ready'),
    path('',views.map, name='map'),
    path('',views.result,name='result'),
    path('',views.login1,name='login1'),
    path('',views.register,name='register'),
    path('',views.logout,name='logout'),
    path('',views.art,name='art'),
    path('',views.balancegame,name='balancegame'),
    path('',views.health,name='health'),
    path('',views.other,name='other'),
    path('',views.base1, name='base1'),
    path('',views.base2, name='base2'),
    path('',views.test, name='test'),
]
