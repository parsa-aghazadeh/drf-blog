# Generated by Django 5.1.2 on 2024-11-11 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_backend', '0003_rename_token_user_forget_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
