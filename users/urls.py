from django.urls import path

from . import views

urlpatterns = [
    path("get/all", views.get_all_users),
    path("get/<str:pk>", views.get_user_by_id),
    path("sign-up/email/", views.sign_up_user),
    path("update/<str:pk>", views.update_user),
    path("delete/<str:pk>", views.delete_user),
    path("login/api/token/email/", views.login_user),
    path("logout/api/token/", views.logout_user),
    path('send-otp', views.send_otp, name='send-otp'),
    path('verify-otp', views.verify, name='verify-otp'),

]
