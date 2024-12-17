from django.db import models
from coelinks.profiles.formatChecker import ContentTypeRestrictedFileField
from coelinks.profiles.models import User, Admin, Regular, Enterprise
from django.utils.translation import gettext_lazy as _
from . import managers
import os

# Create your models here.


def document_directory_path(instance, filename):

    return 'id_cards/user_{0}/{1}'.format(instance.client_num, filename)


class IDVerify(models.Model):
    client_num = models.IntegerField()
    user_id = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    dob = models.CharField(max_length=30, null=True, blank=True)
    expiry_date = models.CharField(max_length=30, null=True, blank=True)
    idcard = ContentTypeRestrictedFileField(upload_to=document_directory_path,
                                             content_types=['image/bmp', 'image/gif', 'image/jpeg', 'image/png', ],
                                             max_upload_size=52428800, blank=True, null=True)

    def __str__(self):
        return str(self.user_id)

