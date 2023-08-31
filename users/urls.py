from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)
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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
