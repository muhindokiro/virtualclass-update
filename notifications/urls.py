from django.urls import path
from notifications.views import ShowNotifications


urlpatterns = [
    path('notifications', ShowNotifications, name='notifications'),

]