from django.urls import path
from . import views

urlpatterns = [
    path('', views.account_list, name='account_list'),
    path('add/', views.add_account, name='add_account'),
    path('<int:pk>/', views.account_detail, name='account_detail'),
]
