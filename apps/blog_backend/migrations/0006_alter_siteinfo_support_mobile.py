# Generated by Django 5.1.2 on 2024-11-16 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_backend', '0005_siteinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteinfo',
            name='support_mobile',
            field=models.IntegerField(max_length=11),
        ),
    ]
