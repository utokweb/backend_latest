# Generated by Django 3.2 on 2020-09-22 08:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('videoserver_talk', '0043_frameid'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='frameid',
            unique_together={('user', 'frameId')},
        ),
        migrations.RemoveField(
            model_name='frameid',
            name='stickerCount',
        ),
        migrations.RemoveField(
            model_name='frameid',
            name='stickerId',
        ),
        migrations.CreateModel(
            name='StickerId',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stickerId', models.IntegerField(default=0)),
                ('stickerCount', models.IntegerField(default=0)),
                ('postId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='postSticker', to='videoserver_talk.fileupload')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='userIdSticker', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'stickerId')},
            },
        ),
    ]
