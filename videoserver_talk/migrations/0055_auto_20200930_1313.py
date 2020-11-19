# Generated by Django 3.2 on 2020-09-30 13:13

from django.db import migrations, models
import django.db.models.deletion
import youtalk.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('videoserver_talk', '0054_alter_firebasenotification_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='MusicTracks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('musicFile', models.FileField(blank=True, null=True, storage=youtalk.storage_backends.PublicMediaStorage(), upload_to='')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='fileupload',
            name='musicTrack',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='musicTrack', to='videoserver_talk.musictracks'),
        ),
    ]
