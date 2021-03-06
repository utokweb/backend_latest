# Generated by Django 3.2 on 2020-09-04 06:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('videoserver_talk', '0002_auto_20200901_0857'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowerModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like', models.SmallIntegerField(blank=True, default=0, null=True)),
                ('follower_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followerId', to=settings.AUTH_USER_MODEL)),
                ('following_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followingId', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
