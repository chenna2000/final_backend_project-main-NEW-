# Generated by Django 4.2.15 on 2024-10-08 10:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0005_alter_companyincharge_user_alter_consultant_user_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
