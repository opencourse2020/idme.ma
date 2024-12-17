from django.contrib import admin
from . import models

model_objects = (
    models.IDVerify,
    )

for m in model_objects:
    admin.site.register(m)

# Register your models here.
