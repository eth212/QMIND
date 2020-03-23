from django.urls import path, include
from . import views

app_name = 'TRMap'
urlpatterns = [
    path('', views.map, name='index')
]
