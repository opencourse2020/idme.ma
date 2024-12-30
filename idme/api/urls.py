from django.urls import path, include, re_path

from . import views

app_name = "idmeapi"


urlpatterns = [
    re_path("idverify/", views.FileUpdateView.as_view(), name="idverify"),
    path("verify/", views.IDVerifyView.as_view(), name="verify"),
    path("sdashboard/", views.ConditionsView.as_view(), name="sdashboard"),

]