# Generated by Django 3.2 on 2020-09-30 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videoserver_talk', '0056_musictracks_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='musictracks',
            old_name='name',
            new_name='albumArt',
        ),
        migrations.AddField(
            model_name='musictracks',
            name='category',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='musictracks',
            name='duration',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='musictracks',
            name='genre',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='musictracks',
            name='musicName',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='musictracks',
            name='popularityCount',
            field=models.IntegerField(default=0.0, null=True),
        ),
        migrations.AddField(
            model_name='musictracks',
            name='singerName',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]