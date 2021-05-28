# Generated by Django 3.2 on 2020-08-30 09:11

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import videoserver_talk.models
import youtalk.storage_backends


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('datafile', models.FileField(upload_to=videoserver_talk.models.user_directory_path)),
                ('thumbnail', models.ImageField(default='', upload_to=videoserver_talk.models.user_directory_path)),
                ('description', models.TextField(blank=True)),
                ('privacy', models.CharField(choices=[('only_me', 'Only Me'), ('private', 'Private'), ('public', 'Public')], default='public', max_length=20)),
                ('likeCount', models.IntegerField(default=0)),
                ('viewCount', models.IntegerField(default=0)),
                ('hashtag', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=1000), blank=True, null=True, size=None)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HashTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hashtag', models.CharField(default='', max_length=20, null=True, unique=True)),
                ('count', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ViewModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=0)),
                ('postId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='postId', to='videoserver_talk.fileupload')),
            ],
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=500, null=True, unique=True)),
                ('bio', models.TextField(blank=True)),
                ('fullName', models.CharField(blank=True, max_length=20)),
                ('profilePic', models.ImageField(default='', storage=youtalk.storage_backends.PublicMediaStorage(), upload_to='')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like', models.SmallIntegerField(blank=True, default=0, null=True)),
                ('postId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='post', to='videoserver_talk.fileupload')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('postId', 'user', 'like')},
            },
        ),
    ]