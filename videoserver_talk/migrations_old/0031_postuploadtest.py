# Generated by Django 3.2 on 2020-09-17 23:20

from django.db import migrations, models
import youtalk.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('videoserver_talk', '0030_fileupload_profid'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostUploadTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('downloadUrl', models.FileField(storage=youtalk.storage_backends.PublicMediaStorage(), upload_to='')),
                ('fileName', models.CharField(blank=True, max_length=20, null=True)),
                ('post_format', models.CharField(blank=True, max_length=20, null=True)),
                ('durationMs', models.CharField(blank=True, max_length=20, null=True)),
                ('frameRate', models.IntegerField(default=0)),
                ('category', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
    ]
