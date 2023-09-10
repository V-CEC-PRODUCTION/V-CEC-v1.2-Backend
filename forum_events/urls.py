from django.urls import path
from .views import *

urlpatterns = [
    path('create-form/',create_forms,name='create-form'),
]
