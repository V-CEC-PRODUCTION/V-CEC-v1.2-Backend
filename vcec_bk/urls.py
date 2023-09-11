from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/auth/', include('users.urls')),
    path('notices/nav/', include('notices.urls')),
    path('homepage/', include('homepage_images.urls')),
    path('staff/info/',include('staff_info.urls')),
    path('highlights/cec/',include('highlights_cec.urls')),
    path('gallery/cec/',include('gallery_cec.urls')),
    path('forum/events/',include('forum_events.urls')),
    path('forum/announcements/',include('forum_announcements.urls'))
]

urlpatterns += staticfiles_urlpatterns()    