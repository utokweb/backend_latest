# Generated by Django 3.2 on 2020-09-04 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videoserver_talk', '0006_alter_followermodel_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonenumber',
            name='followerCount',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='followingCount',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
