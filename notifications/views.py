from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from virtual.decorators import allowed_users
from notifications.models import Notification
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import Group

# Create your views here.

@login_required(login_url="login")
@allowed_users(allowed_roles=['lecturer'])
def ShowNotifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-date')
    Notification.objects.filter(user=user, is_seen=False).update(is_seen=True)

    template = loader.get_template('notifications.html')

    context = {
        'notifications': notifications,
    }
    print(context)
    return HttpResponse(template.render(context, request))
