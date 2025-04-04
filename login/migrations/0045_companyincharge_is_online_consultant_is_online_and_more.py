# Generated by Django 5.1.5 on 2025-03-26 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0044_remove_companyincharge_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyincharge',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='consultant',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='jobseeker',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='new_user',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='universityincharge',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
    ]
