from .models import UploadedInputsInfo
from rest_framework import serializers

class UploadedInputsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedInputsInfo
        fields = ['user_names', 'file_names', 'output_status', 'date']
