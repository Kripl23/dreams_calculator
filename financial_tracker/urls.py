from django.urls import path
from . import views

urlpatterns = [
    path('', views.account_list, name='account_list'),
    path('add/', views.add_account, name='add_account'),
    path('<int:pk>/', views.account_detail, name='account_detail'),
    path('<int:pk>/events/add/', views.add_event, name='add_event'),
    path('events/<int:pk>/delete/', views.delete_event, name='delete_event'),
]
