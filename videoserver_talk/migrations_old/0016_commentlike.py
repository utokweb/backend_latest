# Generated by Django 3.2 on 2020-09-06 17:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('videoserver_talk', '0015_replymodel_profid'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like', models.SmallIntegerField(blank=True, default=0, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('commentId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='commentLike', to='videoserver_talk.commentmodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_comment', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('commentId', 'user')},
            },
        ),
    ]