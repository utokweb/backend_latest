# Generated by Django 3.2 on 2020-09-05 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('videoserver_talk', '0010_commentmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReplyModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('commentId', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='commentId', to='videoserver_talk.commentmodel')),
            ],
        ),
    ]