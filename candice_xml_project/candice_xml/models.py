from django.db import models

# Create your models here.
class UploadedInputsInfo(models.Model):
    user_names = models.CharField(max_length=10000000)
    file_names = models.CharField(max_length=10000000)
    output_status = models.CharField(max_length=10000000)
    date = models.CharField(max_length=10000000)