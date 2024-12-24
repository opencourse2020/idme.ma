from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class JsonFormMixin:
    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse(form.data)

    def form_invalid(self, form):
        data = {
            "success": False,
            "errors": {k: v[0] for k, v in form.errors.items()},
        }
        return JsonResponse(data, status=400)


class RegularRequiredMixin(PermissionRequiredMixin):
    permission_required = "profiles.access_regular_pages"
    login_url = reverse_lazy("profiles:403")


class AdminRequiredMixin(PermissionRequiredMixin):
    permission_required = "profiles.access_admin_pages"
    login_url = reverse_lazy("profiles:403")


class AdminAllowedMixing(PermissionRequiredMixin):
    permission_required = ("", "", "", "", "")
    login_url = reverse_lazy("profiles:403")


class MFAVerifiedMixing(object):
    def get_object(self):
        status = False

        if self.request.user.mfa_enabled and self.request.user.mfa_checked:
            status = True
        elif not self.request.user.mfa_enabled:
            status = True

        return status


class CustomLoginRequiredMixin(LoginRequiredMixin, MFAVerifiedMixing):
    def dispatch(self, request, *args, **kwargs):
        mfa_check = self.get_object()
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        elif not mfa_check:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)