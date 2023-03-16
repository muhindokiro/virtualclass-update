from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", views.home, name="home"),
    path("camera/", views.cameraView, name="camera"),
    path("register/", views.registerPage, name="register"),
    path("profile/", views.userProfile, name="profile"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("student/", views.studentPage, name="student"),
    path('<uuid:post_id>/delete', views.delete, name='delete'),
    path('<uuid:post_id>/view', views.view, name='postview'),
    path('<uuid:post_id>', views.PostDetails, name='postdetails'),
    path("lecturer/", views.lecturerPage, name="lecturer"),
    path("lecturer/upload/", views.upload_file, name="upload_file"),
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
