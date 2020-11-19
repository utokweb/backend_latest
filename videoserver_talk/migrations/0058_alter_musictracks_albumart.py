# Generated by Django 3.2 on 2020-10-01 10:49

from django.db import migrations, models
import youtalk.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('videoserver_talk', '0057_auto_20200930_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='musictracks',
            name='albumArt',
            field=models.FileField(blank=True, null=True, storage=youtalk.storage_backends.PublicMediaStorage(), upload_to=''),
        ),
    ]
