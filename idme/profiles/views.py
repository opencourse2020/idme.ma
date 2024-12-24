import io
import base64
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import (
    UpdateView,
    RedirectView,
    CreateView,
    View,
    TemplateView,
    DetailView,
    ListView,
    DeleteView,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from tablib import Dataset
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Permission, Group
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from . import forms, models
from .mixins import (RegularRequiredMixin, AdminRequiredMixin, AdminAllowedMixing, JsonFormMixin, CustomLoginRequiredMixin)
from django.contrib import messages
from datetime import datetime, date, timedelta
User = get_user_model()
import pyotp
import qrcode


class ProfileActivateView(AdminRequiredMixin, LoginRequiredMixin, UpdateView):
    model = User
    fields = ["is_active"]
    template_name = "profiles/activate_form.html"
    formset_class = None
    success_url = reverse_lazy("profiles:profile")

    # def form_valid(self, form):
    #     pk = self.kwargs.get("pk")
    #     if self.request.user.pk==pk:
    #         form.save()
    #     else:
    #         raise ValidationError(_("You don't have authorization to make that change"))
    #     return super().form_valid(form)

    def get_context_data(self, **kwargs):

        kwargs["title"] = _("Deactivate your Account")

        return super().get_context_data(**kwargs)


class ProfilesUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["username", "first_name", "last_name", "picture"]
    template_name = "profiles/user_form.html"
    formset_class = None
    success_url = reverse_lazy("profiles:profile")

    # def form_valid(self, form):
    #     pk = self.kwargs.get("pk")
    #     if self.request.user.pk==pk:
    #         form.save()
    #     else:
    #         raise ValidationError(_("You don't have authorization to make that change"))
    #     return super().form_valid(form)
    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs["title"] = _("Personal Info")

        return super().get_context_data(**kwargs)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["email"]
    formset_class = None

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = self.formset_class(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context["formset"] = self.formset_class(instance=self.object)

        kwargs["title"] = _("Your Profile")

        return context

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        formset = context["formset"]
        user = self.request.user
        if formset.is_valid():

            response = super().form_valid(form)
            formset.instance = self.object
            formset.save()
            return response
        else:
            return super().form_invalid(form)


class LanguageUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = forms.LanguageForm
    template_name = "profiles/language_form.html"
    success_url = reverse_lazy("profiles:profile")

    def get_context_data(self, **kwargs):

        kwargs["title"] = _("Language")

        return super().get_context_data(**kwargs)


class AdminUpdateView(ProfileUpdateView):
    template_name = "profiles/profile_form.html"
    success_url = reverse_lazy("profiles:profile")
    formset_class = forms.AdminFormSet

    def get_context_data(self, **kwargs):

        kwargs["title"] = _("Your Profile")

        return super().get_context_data(**kwargs)

    # def get_form_kwargs(self):
    #     kwargs = super(ParentUpdateView, self).get_form_kwargs()
    #     year = 1930
    #     YEARS = [year + i for i in range(70)]
    #     kwargs.update({"yearofbirth": self.request.user.professor})
    #     return kwargs

class RegularUpdateView(ProfileUpdateView):
    template_name = "profiles/profile_form.html"
    success_url = reverse_lazy("profiles:profile")
    formset_class = forms.RegularFormSet

    def get_context_data(self, **kwargs):

        kwargs["title"] = _("Your Profile")

        return super().get_context_data(**kwargs)


class ProfileDetailView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/profile.html"


class ProfileView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if hasattr(self.request.user, "admin"):
            return reverse_lazy("profiles:admin")
        elif hasattr(self.request.user, "regular"):
            return reverse_lazy("profiles:regular")

        return super().get_redirect_url(*args, **kwargs)


class DispatchLoginView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if hasattr(self.request.user, "admin"):
            return reverse_lazy("idmeapi:sdashboard")
        elif hasattr(self.request.user, "regular"):
            return reverse_lazy("idmeapi:sdashboard")
        else:
            return reverse_lazy("idmeapi:sdashboard")

        return super().get_redirect_url(*args, **kwargs)


class ReviewCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.ReviewForm

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse_lazy("core:detail", args=[pk])

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)


class ContactRequestView(SingleObjectMixin, View):
    model = models.User

    def post(self, *args, **kwargs):
        admin = self.get_object()
        admin.contacts_requests += 1
        admin.save()
        return HttpResponse()


class EnterpriseCreateView(LoginRequiredMixin, CreateView):
    model = models.Enterprise
    form_class = forms.EnterpriseForm
    template_name = "profiles/enterprise_edit.html"
    success_url = reverse_lazy("idmeapi:sdashboard")


class EnterpriseEditView(LoginRequiredMixin, CreateView):
    model = models.Enterprise
    form_class = forms.EnterpriseForm
    template_name = "profiles/enterprise_edit.html"
    success_url = reverse_lazy("idmeapi:sdashboard")


class UserDetailView(DetailView, SingleObjectMixin):
    model = models.User
    template_name = "profiles/user_detail.html"


class FreecoursesView(TemplateView):
    template_name = "../templates/freecourses.html"


class ForbiddenView(TemplateView):
    template_name = "../templates/403.html"


class ConditionsView(TemplateView):
    template_name = "../templates/conditions.html"


class PrivacyView(TemplateView):
    template_name = "../templates/privacy.html"


def verify_2fa_otp(user, otp):
    totp = pyotp.TOTP(user.mfa_secret)
    if totp.verify(otp):
        user.mfa_enabled = True
        user.save()
        return True
    return False


class ProfilesMFAView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/profile_otp.html"

    # success_url = reverse_lazy("profiles:profile")

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs["title"] = _("Personal Info")
        otp_uri = pyotp.totp.TOTP(user.mfa_secret).provisioning_uri(
            name=user.email,
            issuer_name="Idme.ma"
        )

        qr = qrcode.make(otp_uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")

        buffer.seek(0)
        qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")
        # kwargs["qr_code"] = qr_code

        kwargs["qr_code_data_uri"] = f"data:image/png;base64,{qr_code}"

        return super().get_context_data(**kwargs)



def verify_mfa(request):
    if request.method == 'POST':
        otp = request.POST.get('otp_code')
        user_id = request.POST.get('user_id')
        if not user_id:
            messages.error(request, 'Invalid user id. Please try again.')
            return render(request, 'profiles/verify_otp.html', {'user_id': user_id})

        user = models.User.objects.get(id=user_id)
        if verify_2fa_otp(user, otp):
            if request.user.is_authenticated:
                messages.success(request, '2FA enabled successfully !')
                return redirect('profiles:profile')

            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('profiles:profile')
        else:
            if request.user.is_authenticated:
                messages.error(request, 'Invalid OTP code. Please try again.')
                return redirect('profiles:profile')
            messages.error(request, 'Invalid OTP code. Please try again.')
            return render(request, 'profiles/verify_otp.html', {'user_id': user_id})

    return render(request, 'profiles/verify_otp.html', {'user_id': user_id})


@login_required
def disable_2fa(request):
    user = request.user
    if user.mfa_enabled:
        user.mfa_enabled = False
        user.save()
        messages.success(request, "Two-Factor Authentication has been disabled.")
        return redirect('profiles:profile')
    else:
        messages.info(request, "2FA is already disabled.")
    return redirect('profiles:profile')
