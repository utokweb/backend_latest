# Generated by Django 3.2 on 2020-09-11 07:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('videoserver_talk', '0024_auto_20200911_0713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replylike',
            name='replyId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replyLike', to='videoserver_talk.replymodel'),
        ),
    ]
