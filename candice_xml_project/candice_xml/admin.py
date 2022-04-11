from django.contrib import admin
from .models import UploadedInputsInfo

# Register your models here.
@admin.register(UploadedInputsInfo)
class UploadedInputsInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_names', 'file_names', 'output_status', 'date']
