from django.urls import path
from .views import *

urlpatterns = [
    path('directory/', staff_list.as_view()),
    path('directory/get/<dep>', staff_dep.as_view()),
    path('directory/search/<dep>', search_staff_dep.as_view()),
    path('directory/search/all/<search>', full_staff_search.as_view()),
    path('directory/<int:pk>/', staff_detail),
    path('directory/delete/<int:pk>/', staff_delete)
]