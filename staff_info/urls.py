from django.urls import path
from .views import *

urlpatterns = [
    path('directory/', staff_list),
    path('directory/get/<dep>', staff_dep),
    path('directory/search/<dep>', search_staff_dep),
    path('directory/search/all/<search>', full_staff_search),
    path('directory/<int:pk>/', staff_detail),
    path('directory/delete/<int:pk>/', staff_delete)
]