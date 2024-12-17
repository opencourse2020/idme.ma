from django.db import models


class EnterpriseManager(models.Manager):
    use_for_related_fields = True

    def created_by(self, enterprise):
        return self.filter(enterprise=enterprise)
