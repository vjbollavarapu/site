from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('', views.newsletter_list, name='newsletter_list'),
    path('<uuid:pk>/', views.newsletter_detail, name='newsletter_detail'),
]

