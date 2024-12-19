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

from django.urls import reverse_lazy
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from guardian.shortcuts import assign_perm
from guardian.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from . import models, forms
from .mixins import JsonFormMixin
from .serializers import FileSerializer
from idme.profiles.models import Admin, User, Regular, Enterprise
from django.conf import settings
# Data analytics librairies
import json
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import seaborn as sns
from datetime import datetime as dt
from .id_recognize import idrecognize
from .tools import verifySignature
from obfuskey import Obfuskey, alphabets
# Create your views here.

# Set the lenght of the hash key
obfuscator = Obfuskey(alphabets.BASE36, key_length=18)

class IDVerifyView(TemplateView):
    # model = models.IDVerify
    # form_class = forms.IDVerifyCreateForm
    template_name = "idmeapi/idverify.html"
    # success_url = reverse_lazy("coeanalytics:analytictypes:list")
    def get_context_data(self, **kwargs):
        # clientid = int(self.kwargs.get("client_id"))
        clientid = int(self.request.user.id)
        user_id = "{:06d}".format(int(self.kwargs.get("user_id")))
        clientid = "{:06d}".format(dt.now().hour*10000+dt.now().minute*100+dt.now().second)
        sec = "{:02d}".format(dt.now().second)
        client_user_id = obfuscator.get_value("{}XX{}XX{}".format(user_id, clientid, sec))
        kwargs["clientid"] = client_user_id
        return super(IDVerifyView, self).get_context_data(**kwargs)

class FileUpdateView(CreateView, JsonFormMixin):
  # parser_classes = (MultiPartParser, FormParser)
  # parser_classes = (FileUploadParser,)

  @csrf_exempt
  def post(self, request, *args, **kwargs):
    # file_serializer = FileSerializer(data=request.data)


    # if file_serializer.is_valid():
    print("Step 1")
    filename = request.FILES['file']
    side = int(request.POST.get("side"))
    client_user_id = request.POST.get("cid")
    clientuser = obfuscator.get_key(int(client_user_id))
    client = int(clientuser.split("XX")[1])
    print(client)
    obj, created = models.IDVerify.objects.update_or_create(
        client_user=clientuser, defaults={'client_num': client, 'idcard': filename})
    result = idrecognize(str(client), side)
    if result:
        if side == 1:
            identification = result.get("Identity")
            if identification:
                identification.strip()
            else:
                identification = result.get("Driver's License Number")
            name = result.get("Name")
            city = result.get("City of Birth")
            dob = result.get("Date of Birth (DOB)")
            expiry_date = result.get("Expiration Date (EXP)")
            obj, created = models.IDVerify.objects.update_or_create(
                client_user=clientuser,
                defaults={'user_id': identification, 'name': name, 'birth_city': city, 'dob': dob,
                          'expiry_date': expiry_date, 'client_num': client}
            )
            result = {'id': identification, 'name': name, 'city': city, 'dob': dob, 'expire': expiry_date}
        elif side == 2:
            identification = result.get("Identity").strip()
            address = result.get("Address")
            gender = result.get("Gender")
            obj, created = models.IDVerify.objects.update_or_create(
                client_user=clientuser,
                defaults={'address': address, 'gender': gender, 'client_num': client}
            )
            result = {'id': identification, 'address': address, 'gender': gender}
        # if expiry_date_text.find("-"):
        #     expiry_date_text = expiry_date_text.replace("-", "/")
        # print(expiry_date_text)
        # expiry_date = datetime.strptime(expiry_date_text, '%m/%d/%y').strftime('%m/%d/%Y')
        # print("expire:", expiry_date)
        # license_number = result.get("Driver's License Number")
        # print("user_id:", license_number)

    data = result

    return JsonResponse(data)
    # else:
    #     return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConditionsView(LoginRequiredMixin, TemplateView):
    template_name = "../templates/conditions.html"