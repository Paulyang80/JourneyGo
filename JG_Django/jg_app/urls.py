from django.urls import path

from jg_app import views


urlpatterns = [
    path('',views.index,name='index'),
    path('',views.result,name='result'),
    path('',views.friends,name='friends'),
    path('',views.searchRec,name='searchRec'),
    path('',views.startDropDown,name='startDropDown'),
    path('',views.setting,name='setting'),
]

