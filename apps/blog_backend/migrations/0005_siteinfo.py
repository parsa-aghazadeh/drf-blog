# Generated by Django 5.1.2 on 2024-11-16 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_backend', '0004_comment_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('support_email', models.EmailField(max_length=254)),
                ('support_mobile', models.IntegerField()),
            ],
        ),
    ]
