from django.urls import path
from . import views

app_name = 'waitlist'

urlpatterns = [
    path('', views.waitlist_list, name='waitlist_list'),
    path('<uuid:pk>/', views.waitlist_detail, name='waitlist_detail'),
]

