# Generated by Django 3.2 on 2020-09-28 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videoserver_talk', '0051_firebasenotification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firebasenotification',
            name='token',
            field=models.CharField(default='', max_length=200, null=True, unique=True),
        ),
    ]
