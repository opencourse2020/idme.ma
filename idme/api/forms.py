from django import forms
from django.utils.translation import gettext_lazy as _
from django.forms.models import inlineformset_factory
from . import models


class IDVerifyCreateForm(forms.ModelForm):
    class Meta:
        model = models.IDVerify
        fields = ["idcard_f"]

        labels = {
            "idcard": _("ID Card")
        }