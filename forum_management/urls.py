from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateForum.as_view(), name='create-forum'),
    path('update/<str:pk>', views.UpdateForumdetails.as_view(), name='update-forum'),
    path('get/all/', views.GetAllUsers.as_view(), name='get-all-forums'),
    path('get/individual/<str:pk>/', views.GetUserById.as_view(), name='get-forum-by-id'),
    path('delete/<str:pk>', views.DeleteForum.as_view(), name='delete-forum'),
    path('images/<str:pk>/file/', views.ImageFile.as_view(), name='image-file'),
    path('images/<str:pk>/thumbnail/', views.ThumbnailFile.as_view(), name='thumbnail-file'),
    path('login/api/token/', views.LoginUserGoogle.as_view(), name='login-forum'),
    path('logout/api/token/', views.LogoutUser.as_view(), name='logout-forum'),
    path('refresh/api/token/', views.RequestAccessToken.as_view(), name='refresh-token'),
    path('validate/access/token/', views.ValidateTokenView.as_view(), name='validate-token'),
    path('update/profile/image/<str:pk>', views.UpdateForumImage.as_view(), name='update-profile-image'),
    path('get/roles/', views.AllforumRoles.as_view(), name='get-all-roles'),
    path('get/list/',views.GetForumList.as_view(),name='get-forum-list'),
]
