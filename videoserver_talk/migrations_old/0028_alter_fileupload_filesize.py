# Generated by Django 3.2 on 2020-09-11 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videoserver_talk', '0027_auto_20200911_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='fileSize',
            field=models.CharField(default=0, max_length=100, null=True),
        ),
    ]