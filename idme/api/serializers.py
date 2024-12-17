from rest_framework import serializers
from .models import IDVerify


class FileSerializer(serializers.ModelSerializer):
    class Meta():
        model = IDVerify
        fields = ('user_id', 'name', 'address', 'dob', 'expiry_date', 'idcard')
