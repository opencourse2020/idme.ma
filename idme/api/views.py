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
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileSerializer
from django.urls import reverse_lazy
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from guardian.shortcuts import assign_perm
from guardian.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from .pmf.pmf_analysis import GrowthAccounting, Cohorts
from . import models, forms
from .mixins import EnterprisePermissionRequiredMixin, JsonFormMixin, FormsetMixin
from coelinks.profiles.models import Enterprise
from django.conf import settings
# Data analytics librairies
import json
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import seaborn as sns
from datetime import datetime
from .id_recognize import idrecognize
from .tools import verifySignature
# Create your views here.


class IDVerifyView(TemplateView):
    # model = models.IDVerify
    # form_class = forms.IDVerifyCreateForm
    template_name = "coeanalytics/idverify.html"
    # success_url = reverse_lazy("coeanalytics:analytictypes:list")


class FileUpdateView(CreateView, JsonFormMixin):
  # parser_classes = (MultiPartParser, FormParser)
  # parser_classes = (FileUploadParser,)

  @csrf_exempt
  def post(self, request, *args, **kwargs):
    # file_serializer = FileSerializer(data=request.data)


    # if file_serializer.is_valid():
    print("Step 1")
    filename = request.FILES['file']
    client = 1
    obj, created = models.IDVerify.objects.update_or_create(
        client_num=client, defaults={'idcard': filename})
    print(filename.name)

    result = idrecognize(str(client))
    print(result)
    if result:
        name = result.get("Name")
        print("Name:", name)
        address = result.get("Address")
        print("Address:", address)
        dob = result.get("Date of Birth (DOB)")
        # if dob_text.find("-"):
        #     dob_text = dob_text.replace("-", "/")
        # print(dob_text)
        # dob = datetime.strptime(dob_text, '%m/%d/%y').strftime('%m/%d/%Y')
        print("DOB:", dob)
        expiry_date = result.get("Expiration Date (EXP)")
        # if expiry_date_text.find("-"):
        #     expiry_date_text = expiry_date_text.replace("-", "/")
        # print(expiry_date_text)
        # expiry_date = datetime.strptime(expiry_date_text, '%m/%d/%y').strftime('%m/%d/%Y')
        print("expire:", expiry_date)
        license_number = result.get("Driver's License Number")
        print("user_id:", license_number)

        obj, created = models.IDVerify.objects.update_or_create(
            client_num=1,
            defaults={'user_id': license_number, 'name': name, 'address': address, 'dob': dob, 'expiry_date': expiry_date}
        )
        result = {'id': license_number, 'name': name, 'address': address, 'dob': dob, 'expire': expiry_date}

    data = result

    return JsonResponse(data)
    # else:
    #     return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
