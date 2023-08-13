from django.urls import path
from . import views

urlpatterns = [
    path("get/all", views.get_all_users),
    path("get/<str:pk>", views.get_user_by_id),
    path("create", views.create_user),
    path("update/<str:pk>", views.update_user),
    path("delete/<str:pk>", views.delete_user),
    path("login", views.login_user),
    path("logout", views.logout_user),
]
