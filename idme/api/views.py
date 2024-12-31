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
from idme.profiles.models import Admin
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
from .tools import verifySignature, check_name, check_ip
from obfuskey import Obfuskey, alphabets
# Create your views here.

# Set the lenght of the hash key
obfuscator = Obfuskey(alphabets.BASE36, key_length=34)

class IDVerifyView(TemplateView):
    # model = models.IDVerify
    # form_class = forms.IDVerifyCreateForm
    template_name = "idmeapi/idverify.html"
    # success_url = reverse_lazy("coeanalytics:analytictypes:list")
    def get_context_data(self, **kwargs):
        postData = self.request.GET
        kwargs["userid"] = postData.get("user").upper()  #clfid: client for user id
        client_id = int(postData.get('client'))

        kwargs["fname"] = postData.get('fname')
        lname = postData.get('lname')
        kwargs["email"] = postData.get('email')
        kwargs["phone"] = postData.get('phone')
        kwargs["lname"] = lname

        # convert last name to ASCII value and create a unique client/user ID
        # from the last name of the user, the client id and (minutes+seconds)
        lname_upper = lname.upper()
        nchars = len(lname_upper)
        num_val = sum(ord(lname_upper[byte]) << 8 * (nchars - byte - 1) for byte in range(nchars))
        lname_left = str(num_val)[:20]
        int_lname_left = int(lname_left)
        user_id = "{:020d}".format(int_lname_left)
        clientid = "{:08d}".format(client_id)
        call_time = "{:04d}".format(dt.now().minute * 100 + dt.now().second)
        client_user_id = "{}X{}X{}".format(user_id, clientid, call_time)
        clientuser = obfuscator.get_value(client_user_id)


        # obj, created = models.IDVerify.objects.update_or_create(
        #     client_user=client_user_id, defaults={'temp_user_id': userid, 'temp_firstname': fname, 'temp_lastname': lname,
        #                                      'user_email': email, 'user_phone': phone, 'client_num': client})
        # clientid = "{:08d}".format(obj.client_num)
        # user_id = "{:020d}".format(num_val)
        # num_chars = "{:02d}".format(nchars)
        # clientid = "{:06d}".format(dt.now().hour*10000+dt.now().minute*100+dt.now().second)
        # call_time = "{:04d}".format(dt.now().minute*100+dt.now().second)
        # client_user_id = obfuscator.get_value("{}X{}X{}".format(user_id, clientid, num_chars))
        kwargs["clientid"] = clientuser
        return super(IDVerifyView, self).get_context_data(**kwargs)

class FileUpdateView(CreateView, JsonFormMixin):
  # parser_classes = (MultiPartParser, FormParser)
  # parser_classes = (FileUploadParser,)

  @csrf_exempt
  def post(self, request, *args, **kwargs):
    # file_serializer = FileSerializer(data=request.data)

    # Get IP Address
    ip_address = check_ip(request)

    # get dat from template
    filename = request.FILES['file']
    side = int(request.POST.get("side"))
    client_user_id = request.POST.get("cid")
    temp_userid = request.POST.get("custid")
    temp_fname = request.POST.get("fname")
    temp_lname = request.POST.get("lname")
    temp_email = request.POST.get("custem")
    temp_phone = request.POST.get("custtel")

    clientuser = obfuscator.get_key(int(client_user_id))
    client_user = clientuser.split("X")
    customer = int(client_user[0])
    client_id = int(client_user[1])
    call_time = int(client_user[2])
    client = Admin.objects.get(pk=client_id)

    # clientuser_id = str(userid) + "@" + str(client)
    if side == 1:
        obj, created = models.IDVerify.objects.update_or_create(
            client_user=clientuser, defaults={'idcard_f': filename, 'ip_address': ip_address,
                                              'temp_user_id': temp_userid, 'temp_firstname': temp_fname,
                                              'temp_lastname': temp_lname, 'user_email': temp_email,
                                              'user_phone': temp_phone, 'client_num': client})
    elif side == 2:
        obj, created = models.IDVerify.objects.update_or_create(
            client_user=clientuser, defaults={'idcard_b': filename, 'ip_address': ip_address,
                                              'temp_user_id': temp_userid, 'temp_firstname': temp_fname,
                                              'temp_lastname': temp_lname, 'user_email': temp_email,
                                              'user_phone': temp_phone, 'client_num': client})

    lname_adjusted = obj.temp_lastname.strip().replace(" ", "_")
    result = idrecognize(str(client), lname_adjusted, side)

    if result:
        if side == 1:
            # temp_user_data = models.IDVerifyTmp.objects.filter(pk=customer).first()

            name_verified = False
            user_id_verified = False
            fname = ""
            lname = ""
            identification = result.get("Identity")
            if identification:
                identification.strip()
            else:
                identification = result.get("Driver's License Number")
            name = result.get("Name")
            city = result.get("City of Birth")
            dob = result.get("Date of Birth (DOB)")
            expiry_date = result.get("Expiration Date (EXP)")

            if check_name(name, temp_fname, temp_lname):
                name_verified = True
                fname = temp_fname
                lname = temp_lname
            if identification.lower() == temp_cin:
                user_id_verified = True

            obj, created = models.IDVerify.objects.update_or_create(
                client_user=clientuser,
                defaults={'user_id': identification, 'lastname': lname, 'birth_city': city,
                          'dob': dob, 'expiry_date': expiry_date, 'firstname': fname, 'name': name,
                          'user_id_verified': user_id_verified, 'name_verified': name_verified}
            )
            result = {'id': identification, 'name': name, 'city': city, 'dob': dob, 'expire': expiry_date}
            # temp_user_data.delete()
        elif side == 2:
            identification = result.get("Identity").strip()
            address = result.get("Address")
            gender = result.get("Gender")
            obj, created = models.IDVerify.objects.update_or_create(
                client_user=clientuser,
                defaults={'address': address, 'gender': gender}
            )
            result = {'address': address, 'gender': gender}
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