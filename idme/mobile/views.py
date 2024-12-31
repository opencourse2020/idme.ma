from django.shortcuts import render
from django.views.generic import (
    CreateView,
    ListView,
    FormView,
    UpdateView,
    DetailView,
    DeleteView,
    TemplateView,
    View,
)
from idme.profiles.models import Admin, User
from idme.api import models
from idme.api.views import IDVerifyView, FileUpdateView
# Create your views here.
