from django.urls import path

from . import views

urlpatterns = [
    path("get/all", views.GetAllUsers.as_view(), name="get-all-users"),
    path("get/<str:pk>", views.GetUserById.as_view(), name="get-user-by-id"),
    path("sign-up/email/", views.SignUpUser.as_view(), name="sign-up-email"),
    path("sign-up/google/", views.SignUpUserGoogle.as_view(), name="sign-up-google"),
    path("update/", views.UpdateUser.as_view(), name="update-user"),
    path("update/photo/", views.UpdateProfilePhotoUser.as_view(), name="update-user-photo"),
    path("delete/<str:pk>", views.DeleteUser.as_view(), name="delete-user"),
    path("login/api/token/email/", views.LoginUser.as_view(), name="login-email"),
    path("login/api/token/google/", views.LoginUserGoogle.as_view(), name="login-email"),
    path("logout/api/token/", views.LogoutUser.as_view(), name="logout"),
    path('send-otp/', views.send_otp, name='send-otp'),
    path('verify-otp/', views.VerifyOtp.as_view(), name='verify-otp'),
    path('refresh/api/token/', views.RequestAccessToken.as_view(), name='refresh-token'),
    path('add/user/detail/', views.UserDetails.as_view(), name='add-user-detail'),
    path('get/user/role/', views.GetUserRole.as_view(), name='get-user-role'),
    path('validate/access/token/', views.ValidateTokenView.as_view(), name='validate-token'),
    path('check/email/exist/', views.CheckEmailExist.as_view(), name='check-email-exist'),
    path('get/user/details/',views.GetUserDetails.as_view(),name='get-user-details'),
    path('api/images/<int:pk>/file/', views.ImageFile.as_view(), name='image-file'),
    path('api/images/<int:pk>/thumbnail/', views.ThumbnailFile.as_view(), name='thumbnail-file')
]
