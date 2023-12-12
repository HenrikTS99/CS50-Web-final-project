from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.shortcuts import render
from .models import User
from .forms import ItemForm
from . import utils
import datetime



def index(request):
    items = request.user.owned_items.all()
    return render(request, "tf2folio/index.html", {
        "items": items
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "tf2folio/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "tf2folio/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username =request.POST["username"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "tf2folio/register.html", {
                "message": "Passwords must match."
            })

        try: 
            user = User.objects.create_user(username=username, password=password)
            user.save()
        except IntegrityError:
            return render(request, "tf2folio/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "tf2folio/register.html")


def new_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.date = datetime.date.today()
            #obj.title = 
            print(utils.create_title(obj))
            obj.save()
            return HttpResponseRedirect(reverse("index"))
    
    return render(request, "tf2folio/new-item.html", {
        "form": ItemForm()
    })
    


