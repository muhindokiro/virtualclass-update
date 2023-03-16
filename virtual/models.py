from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from notifications.models import Notification
from django.db.models.signals import post_save
from django import forms
import uuid
from django.urls import reverse
from django.db.models.signals import post_save,  post_delete

# Create your models here.
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, default="1")
    image = models.ImageField(default='default.jpeg', upload_to='profile_pics/')
    school = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    profession = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f' {self.user.username} Profile'
    
class File(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    pdf = models.FileField(upload_to='files/pdfs/')
    date = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('upload', args=[str(self.id)])

    def __str__(self):
        return self.id


class View(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_view')
    post = models.ForeignKey(
        File, on_delete=models.CASCADE, related_name='post_view')

    def user_viewed_post(sender, instance, *args, **kwargs):
        view = instance
        post = view.post
        sender = view.user
        notify = Notification(post=post, sender=sender,
                              user=post.user, notification_type=1)
        notify.save()

    def user_unview_post(sender, instance, *args, **kwargs):
        view = instance
        post = view.post
        sender = view.user

        notify = Notification.objects.filter(
            post=post, sender=sender, notification_type=1)
        notify.delete()

# views
post_save.connect(View.user_viewed_post, sender=View)
post_delete.connect(View.user_unview_post, sender=View)
