# Generated by Django 3.2 on 2021-05-03 12:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import youtalk.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('videoserver_talk', '0068_auto_20201213_1251'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromotionBanner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('promoFile', models.FileField(blank=True, null=True, storage=youtalk.storage_backends.PromotionBannersStorage(), upload_to='')),
                ('promoName', models.CharField(blank=True, max_length=50, null=True)),
                ('appVersion', models.IntegerField(default=0)),
                ('hashtag', models.CharField(blank=True, max_length=50, null=True)),
                ('category', models.CharField(blank=True, max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('postsCount', models.IntegerField(default=0)),
                ('valid', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.IntegerField(default=0)),
                ('currency', models.CharField(default='INR', max_length=10)),
                ('paytm', models.CharField(blank=True, max_length=10, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='fileupload',
            name='originalAudioUsage',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='fileupload',
            name='shareCount',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='notification',
            name='postId',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='postIdNotification', to='videoserver_talk.fileupload'),
        ),
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transID', models.CharField(default='ORDERID_', max_length=100)),
                ('transType', models.CharField(max_length=100)),
                ('transDesc', models.CharField(max_length=500)),
                ('amount', models.IntegerField(default=0)),
                ('currency', models.CharField(default='INR', max_length=10)),
                ('transTo', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('transStatus', models.CharField(default='ACCEPTED', max_length=100)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='videoserver_talk.wallet')),
            ],
        ),
        migrations.CreateModel(
            name='PromotionNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.CharField(max_length=200)),
                ('topic', models.CharField(blank=True, max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('postID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='videoserver_talk.fileupload')),
            ],
        ),
        migrations.CreateModel(
            name='OriginalAudioPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('originalPost', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='originalPost', to='videoserver_talk.fileupload')),
                ('usingPost', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usingPost', to='videoserver_talk.fileupload')),
                ('usingPostOwner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usingPostOwner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InvitationCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
                ('timesUsed', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
