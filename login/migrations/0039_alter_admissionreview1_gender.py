# Generated by Django 5.1.5 on 2025-03-07 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0038_alter_admissionreview1_hostel_fees'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admissionreview1',
            name='gender',
            field=models.CharField(max_length=10),
        ),
    ]
