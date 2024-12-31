from django.db import models
from .formatChecker import ContentTypeRestrictedFileField
from django.utils.translation import gettext_lazy as _
from . import managers
from idme.profiles.models import User, Admin
from django.utils import timezone
import os

# Create your models here.


def document_directory_path(instance, filename):
    lname = instance.temp_lastname.strip()
    lname = lname.replace(" ", "_")
    return 'id_cards/client_{0}/user_{1}/{2}'.format(instance.client_num.pk, lname, filename)

def picture_directory_path(instance, filename):

    return 'profile_pics/client_{0}/user_{1}/{2}'.format(instance.client_num.pk, instance.temp_lastname, filename)

class IDVerify(models.Model):
    categories = (
        ('M', _("Male")),
        ('F', _("Female")),
    )
    client_num = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True, blank=True)
    customer_id = models.IntegerField(null=True, blank=True)
    user_id = models.CharField(max_length=20, null=True, blank=True)  # for instance CIN or  passport number
    temp_user_id = models.CharField(max_length=20, null=True, blank=True)
    client_user = models.CharField(max_length=34, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    temp_firstname = models.CharField(max_length=50, null=True, blank=True)
    temp_lastname = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    temp_address = models.CharField(max_length=100, null=True, blank=True)
    birth_city = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=categories, default="M")
    dob = models.CharField(max_length=30, null=True, blank=True)
    user_email = models.CharField(max_length=100, null=True, blank=True)
    user_phone = models.CharField(max_length=25, null=True, blank=True)
    expiry_date = models.CharField(max_length=30, null=True, blank=True)
    idcard_f = ContentTypeRestrictedFileField(upload_to=document_directory_path,
                                             content_types=['image/bmp', 'image/gif', 'image/jpeg', 'image/png', ],
                                             max_upload_size=52428800, blank=True, null=True)
    idcard_b = ContentTypeRestrictedFileField(upload_to=document_directory_path,
                                            content_types=['image/bmp', 'image/gif', 'image/jpeg', 'image/png', ],
                                            max_upload_size=52428800, blank=True, null=True)
    user_picture = ContentTypeRestrictedFileField(upload_to=picture_directory_path,
                                              content_types=['image/bmp', 'image/gif', 'image/jpeg', 'image/png', ],
                                              max_upload_size=52428800, blank=True, null=True)
    verification_created_date = models.DateTimeField(auto_now_add=True)
    verification_modified_date = models.DateTimeField(auto_now=True)
    sent = models.BooleanField(default=False)
    name_verified = models.BooleanField(default=False)
    user_id_verified = models.BooleanField(default=False)
    address_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    picture_verified = models.BooleanField(default=False)
    ip_address = models.CharField(max_length=30, null=True, blank=True)
    def __str__(self):
        lname = self.temp_lastname.strip()
        lname = lname.replace(" ", "_")
        return "{}-{}".format(str(self.client_num.pk), lname)


# class IDVerifyTmp(models.Model):
#     client_user = models.CharField(max_length=30, null=True, blank=True)
#     client_num = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True, blank=True)
#     user_id = models.CharField(max_length=20, null=True, blank=True)
#     firstname = models.CharField(max_length=50, null=True, blank=True)
#     lastname = models.CharField(max_length=50, null=True, blank=True)
#     user_email = models.CharField(max_length=100, null=True, blank=True)
#     user_phone = models.CharField(max_length=25, null=True, blank=True)
#
#     def __str__(self):
#         return "{}-{}".format(str(self.client_num.pk), str(self.user_id))