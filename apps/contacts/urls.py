from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    path('', views.contact_list, name='contact_list'),
    path('<uuid:pk>/', views.contact_detail, name='contact_detail'),
]

