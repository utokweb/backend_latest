# Generated by Django 3.2 on 2020-10-01 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videoserver_talk', '0058_alter_musictracks_albumart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='musictracks',
            name='duration',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9),
        ),
    ]
