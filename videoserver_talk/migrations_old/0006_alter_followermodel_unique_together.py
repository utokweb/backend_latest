# Generated by Django 3.2 on 2020-09-04 07:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('videoserver_talk', '0005_auto_20200904_0701'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='followermodel',
            unique_together={('followerId', 'followingId')},
        ),
    ]