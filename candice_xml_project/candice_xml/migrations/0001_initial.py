# Generated by Django 3.2.9 on 2022-01-12 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedInputsInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_names', models.CharField(max_length=10000000)),
                ('file_names', models.CharField(max_length=10000000)),
                ('output_status', models.CharField(max_length=10000000)),
                ('date', models.CharField(max_length=10000000)),
            ],
        ),
    ]