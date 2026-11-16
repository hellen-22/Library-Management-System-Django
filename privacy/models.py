from django.conf import settings
from django.db import models


class Consent(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    value = models.CharField(max_length=3, choices=[('yes', 'yes'), ('no', 'no')])
    withdrawn = models.BooleanField(default=False)
