from django.urls import path, include, re_path
# from django.conf.urls import re_path
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page
from . import views

app_name = "mobile"

urlpatterns = [
    path("dash/", cache_page(60*15)(views.DashboardView.as_view()), name="dashboard"),
    ]