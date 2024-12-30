from django.db import models
from .formatChecker import ContentTypeRestrictedFileField
from django.utils.translation import gettext_lazy as _
from . import managers
from django.utils import timezone
import os

# Create your models here.


def document_directory_path(instance, filename):

    return 'id_cards/user_{0}/{1}'.format(instance.client_num, filename)


class IDVerify(models.Model):
    categories = (
        ('M', _("Male")),
        ('F', _("Female")),
    )
    client_num = models.IntegerField()
    customer_id = models.IntegerField()
    user_id = models.CharField(max_length=20, null=True, blank=True)
    client_user = models.CharField(max_length=24, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    birth_city = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=categories, default="M")
    dob = models.CharField(max_length=30, null=True, blank=True)
    user_email = models.CharField(max_length=100, null=True, blank=True)
    user_phone = models.CharField(max_length=25, null=True, blank=True)
    expiry_date = models.CharField(max_length=30, null=True, blank=True)
    idcard = ContentTypeRestrictedFileField(upload_to=document_directory_path,
                                             content_types=['image/bmp', 'image/gif', 'image/jpeg', 'image/png', ],
                                             max_upload_size=52428800, blank=True, null=True)
    verification_created_date = models.DateTimeField(auto_now_add=True)
    verification_modified_date = models.DateTimeField(auto_now=True)
    sent = models.BooleanField(default=False)
    def __str__(self):
        return "{}-{}".format(str(self.client_num), str(self.customer_id))


class IDVerifyTmp(models.Model):
    client_user = models.CharField(max_length=24, null=True, blank=True)
    client_num = models.IntegerField()
    user_id = models.CharField(max_length=20, null=True, blank=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    user_email = models.CharField(max_length=100, null=True, blank=True)
    user_phone = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return "{}-{}".format(str(self.client_num), str(self.user_id))