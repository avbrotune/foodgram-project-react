# Generated by Django 3.2.3 on 2023-06-16 11:39

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0016_auto_20230616_1137'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Favourite',
            new_name='Favorite',
        ),
    ]