# Generated by Django 3.2 on 2020-09-18 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videoserver_talk', '0032_auto_20200918_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='postuploadtest',
            name='fileSize',
            field=models.IntegerField(default=0),
        ),
    ]