"""
URL configuration for coelinks project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog

from idme.profiles.models import User, Admin, Enterprise
from idme.api.models import IDVerify
# from allauth.models import site
from allauth.mfa.models import Authenticator
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken


from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin

from axes.models import AccessAttempt, AccessFailureLog, AccessLog


# from api.verify.views import FileUpdateView, DocumentScanView, PictureVerifyView, FileUpdatetestView, \
#     DocumentVerifiedView, HeadshotVerifiedView

from idme.profiles.views import ProfileView
# from rest_framework.routers import DefaultRouter
# from api.verify.views import FileUpdateView, DocumentScanView
# from api.chatbot.views import ChatGenerateView
#
# router = DefaultRouter()
#
# router.register(r"verify/", FileUpdateView, basename="verify")
# router.register(r"chat/", ChatGenerateView, basename="chat")

class OTPAdmin(OTPAdminSite):
   pass

admin_site = OTPAdmin(name='OTPAdmin')
# admin_site.register(User)
admin_site.register(TOTPDevice, TOTPDeviceAdmin)
model_objects = (
    User,
    Admin,
    IDVerify,
    # IDVerifyTmp,
    Enterprise,
    Authenticator,
    EmailAddress,
    SocialApp,
    SocialToken,
    SocialAccount,
    AccessAttempt,
    AccessLog,
    AccessFailureLog
    )

for m in model_objects:
    admin_site.register(m)
# admin_site.register(IDVerify)



urlpatterns = [
    # path(settings.ADMIN_URL_DEFENDER, include('defender.urls')), # defender admin
    path(settings.ADMIN_URL, admin_site.urls),
    # path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path("", RedirectView.as_view(pattern_name="profiles:dispatch_login")),
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", ProfileView.as_view()),
    path("idme.apis/", include("idme.api.urls", namespace="idme-apis")),
    path("profiles/", include("idme.profiles.urls", namespace="profiles")),
    path("mobile/", include("idme.mobile.urls", namespace="mobile")),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("i18n/", include("django.conf.urls.i18n")),

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
