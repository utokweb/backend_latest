# Generated by Django 3.2 on 2020-09-22 08:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoserver_talk', '0044_auto_20200922_0835'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='frameid',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='frameid',
            name='postId',
        ),
    ]