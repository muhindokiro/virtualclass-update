from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from virtual.functions.functions import handle_uploaded_file
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required,permission_required
from .decorators import allowed_users,admin_only
from django.views.decorators import gzip
from django.http import StreamingHttpResponse,HttpResponse
from notifications.models import Notification
import cv2
import threading
from django.core.files.storage import FileSystemStorage
from .models import File,Profile,View
from .forms import CreateUserForm,FileForm,UpdateUserForm,ProfileUpdateForm

from django.conf import settings

def home(request):
    return render(request, "home.html")

@login_required(login_url="login")
def userProfile(request):
    notifications = Notification.objects.filter(user = request.user)

    if request.method == 'POST':
        u_form = UpdateUserForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated')
            return redirect('profile')
    else:
        u_form = UpdateUserForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user': request.user,
        'u_form': u_form,
        'p_form': p_form,
        'notifications': notifications
    }
    return render(request, "profile.html", context)

@gzip.gzip_page
def cameraView(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
    return render(request, "camera.html")


@login_required(login_url="login")
@allowed_users(allowed_roles=['student'])
def studentPage(request):
    # user = request.user
    files = File.objects.all()
    # files = File.objects.filter(user=user).order_by('-date')

    return render(request, "student.html", {'files': files})


@login_required(login_url="login")
@allowed_users(allowed_roles=['lecturer'])
def lecturerPage(request):
    files = File.objects.filter(user = request.user)

    # print(context)
    return render(request, "lecturer.html", {'files': files})


def registerPage(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        form = CreateUserForm()
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get("username")
                messages.success(request, "Account was created for " + username)

                group = Group.objects.get(name='student')
                user.groups.add(group)
                
                return redirect("login")

        context = {"form": form}
        return render(request, "register.html", context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.info(request, "Username or Password is incorrect")

        context = {}
        return render(request, "login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("login")


def delete(request, post_id):
    post = File.objects.get(id=post_id)
    post.delete()
    return HttpResponseRedirect(reverse('lecturer'))

@login_required(login_url="login")
@allowed_users(allowed_roles=['lecturer'])
def upload_file(request):
    if request.method == 'POST':
        form =  FileForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save(commit=False)
            new_file.user = request.user
            new_file.save()
            
            return redirect('lecturer')
    else:
        form = FileForm()
    return render(request, "upload.html", {'form': form})

#to capture video class
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@login_required
def view(request, post_id):
    user = request.user
    post = File.objects.get(id=post_id)
    current_views = post.views
    viewed = View.objects.filter(user=user, post=post).count()

    if not viewed:
        view = View.objects.create(user=user, post=post)
        
        current_views = current_views + 1

    else:
        View.objects.filter(user=user, post=post).delete()
        current_views = current_views - 1

    post.views = current_views
    post.save()

    return HttpResponseRedirect(reverse('postdetails', args=[post_id]))


@login_required
def PostDetails(request, post_id):
    post = get_object_or_404(File, id=post_id)
    user = request.user
    profile = Profile.objects.get(user=user)
    favorited = False

    if request.user.is_authenticated:
        profile = Profile.objects.get(user=user)
        # For the color of the favorite button

    template = loader.get_template('post_detail.html')

    context = {
        'post': post,
    }

    return HttpResponse(template.render(context, request))

