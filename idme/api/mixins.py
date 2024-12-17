from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views.generic.edit import ModelFormMixin
from . import forms


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

