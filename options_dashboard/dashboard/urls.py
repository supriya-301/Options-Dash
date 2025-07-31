from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/greeks/', views.get_greeks, name='get_greeks'),
    path('api/ivs/', views.get_ivs, name='get_ivs'),
]
