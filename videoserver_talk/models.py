from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
import random
import string
from django.db import IntegrityError
from django.contrib.postgres.fields import ArrayField
import sys
from django.db import transaction
from youtalk.storage_backends import PublicMediaStorage,PrivateMediaStorage,DPMediaStorage,ThumbnailMediaStorage,MusicTracksStorage,VedioTracksStorage,CameraAssetStorage,PromotionBannersStorage,STORAGE_URL

import firebase_admin
from firebase_admin import credentials
import datetime
from firebase_admin import messaging
from . import utils

cred = credentials.Certificate('fcm.json')
firebase_admin.initialize_app(cred)

def user_directory_path_profile(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'profile_{0}/{1}'.format(instance.user.id, instance.user.username)
    
class PhoneNumber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=500, blank=True,null=True,unique=True)
    bio = models.TextField(blank=True)
    fullName = models.CharField(max_length=20, blank=True,null=False)
    profilePic = models.ImageField(storage=DPMediaStorage(),default="")
    followerCount = models.IntegerField(default=0,blank=True)
    followingCount = models.IntegerField(default=0,blank=True)
    postCount = models.IntegerField(default=0,blank=True)
    elevation = models.IntegerField(null=True,blank=False,default=0)
    gender = models.CharField(max_length=20, blank=True,null=False)
    age = models.IntegerField(default=0,blank=True)
    birthDate = models.DateField(auto_created=False,blank=True,null=True)
    contentConsent = models.BooleanField(default=False,null=False,blank=False)

    def __str__(self):
        return '%s' % (self.user.username)

class InvitationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, blank=False,null=False)
    timesUsed = models.IntegerField(default=0,blank=False,null=False)
    created = models.DateTimeField(auto_now_add=True,blank=False,null=False)  

    def __str__(self):
        return '%s - %s' % (self.user.username,self.code)

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0,blank=False)
    currency = models.CharField(max_length=10, blank=False,null=False,default="INR")
    paytm = models.CharField(max_length=10,blank=True,null=True)

    def __str__(self):
        return '%s - %s' % (self.user.username,self.balance)

class WalletTransaction(models.Model):
    transID = models.CharField(default="ORDERID_",max_length=100, blank=False,null=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transType = models.CharField(max_length=100, blank=False,null=False)
    transDesc = models.CharField(max_length=500, blank=False,null=False)
    amount = models.IntegerField(default=0,blank=False,null=False)
    currency = models.CharField(max_length=10, blank=False,null=False,default="INR")
    transTo = models.CharField(max_length=100, blank=False,null=False) #Wallet,Paytm
    created = models.DateTimeField(auto_now_add=True,blank=False,null=False)
    transStatus = models.CharField(default="ACCEPTED",max_length=100, blank=False,null=False)

    def __str__(self):
        return '%s - %s' % (self.transType,self.amount)

class BlockRequest(models.Model):
    blockedUser = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name='blockedUser')
    blockedBy = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name='blockedBy')
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)    

    class Meta:
        unique_together = ('blockedUser', 'blockedBy')
        
    def __str__(self):
        return '%s-%s' % (self.blockedUser,self.blockedBy)      

class PromotionBanner(models.Model):
    promoFile = models.FileField(storage=PromotionBannersStorage(),blank=True,null=True)
    promoName = models.CharField(max_length=50,blank=True,null=True)
    appVersion = models.IntegerField(null=False,blank=False,default=0)
    hashtag = models.CharField(max_length=50,blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    postsCount = models.IntegerField(null=False,blank=False,default=0)
    valid = models.BooleanField(default=True,null=False,blank=False)
        
    def __str__(self):
        return '%s - HashTag: %s - Version: %s' % (self.promoName,self.hashtag,self.appVersion)           

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.owner.id, filename)

class MusicTracks(models.Model):
    musicFile = models.FileField(storage=MusicTracksStorage(),blank=True,null=True)
    musicName = models.CharField(max_length=30, blank=True,null=True)
    metaData = models.CharField(max_length=30, blank=True,null=True)
    category= models.CharField(max_length=30, blank=True,null=True)
    genre =  models.CharField(max_length=30, blank=True,null=True)
    duration = models.IntegerField(null=True,blank=False,default=0.00)
    popularityCount = models.IntegerField(null=True,blank=False,default=0.00)
    albumArt = models.FileField(storage=PublicMediaStorage(),blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    popularity = models.IntegerField(null=True,blank=False,default=0.00)
    fileSize = models.IntegerField(null=True,blank=False,default=0.00)          


class FileUpload(models.Model):
    privacy_choices = (
        ('only_me', 'Only Me'),
        ('private', 'Private'),
        ('public', 'Public'),
    )
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, to_field='id',on_delete=models.CASCADE)
    datafile = models.FileField(storage=VedioTracksStorage())
    thumbnail = models.ImageField(storage=ThumbnailMediaStorage(),default="")
    description = models.TextField(blank=True)
    privacy = models.CharField(max_length=20,choices=privacy_choices,default="public")
    likeCount = models.IntegerField(default=0)
    viewCount = models.IntegerField(default=0)
    shareCount = models.IntegerField(default=0)
    hashtag = models.TextField(max_length=10001, blank=True)
    commentCount = models.IntegerField(default=0)
    musicTrack = models.ForeignKey(MusicTracks, related_name='musicTrack',on_delete=models.CASCADE,blank=True,null=True)
    fileSize = models.IntegerField(null=True,blank=False,default=0.00)
    latitude = models.DecimalField(max_digits=9, decimal_places=6,blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,blank=True)
    profId = models.ForeignKey(PhoneNumber, to_field='id',on_delete=models.CASCADE,related_name='profIdFileupload')
    category = models.CharField(max_length=20, blank=True,null=True)
    frameId =  models.CharField(max_length=200, blank=True,null=True)
    stickerId = models.CharField(max_length=200, blank=True,null=True)
    reportsCount = models.IntegerField(default=0,null=False,blank=False)
    originalAudioUsage = models.IntegerField(default=0,null=False,blank=False)

    #birthdDate = models.DateField(auto_created = True,blank=True)
class Notification(models.Model):
    fromId = models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name='userNotification')
    toId = models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name='usertoNotification')
    fromUsername = models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name='mainusertoNotification')
    postId = models.ForeignKey(FileUpload,on_delete=models.CASCADE,null=True,related_name='postIdNotification')
    types = models.CharField(max_length=30,blank=True,null=True)
    message = models.CharField(max_length=200,blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)


class PromotionNotification(models.Model):
    title = models.CharField(max_length=200,blank=False,null=False)
    message = models.CharField(max_length=200,blank=False,null=False)
    postID = models.ForeignKey(FileUpload,on_delete=models.CASCADE,null=True)
    topic = models.CharField(max_length=50,blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Title: %s - Message: %s' % (self.title,self.message)     
  
class OriginalAudioPost(models.Model):
    originalPost = models.ForeignKey(FileUpload,on_delete=models.CASCADE,null=False,related_name='originalPost')
    usingPostOwner = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name='usingPostOwner')
    usingPost = models.ForeignKey(FileUpload,on_delete=models.CASCADE,null=False,related_name='usingPost')
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
        
    def __str__(self):
        return '%s-%s' % (self.originalPost,self.usingPost)      

class PostReportRequest(models.Model):
    post = models.ForeignKey(FileUpload,on_delete=models.CASCADE,null=False,related_name='reportedPost')
    reportedBy = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name='reportedBy')
    reportReason = models.CharField(max_length=200,blank=False,null=False)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)

    class Meta:
        unique_together = ('post', 'reportedBy')
        
    def __str__(self):
        return '%s-%s' % (self.post,self.reportedBy)        
    
@receiver(post_save, sender=PostReportRequest, dispatch_uid="update_post_report_count")
def update_reports(sender, instance, **kwargs):
    postData = FileUpload.objects.get(id=instance.post.id)
    postData.reportsCount+=1
    postData.save()


class PostUploadTest(models.Model):
    downloadUrl = models.FileField(storage=CameraAssetStorage())
    fileName = models.CharField(max_length=20, blank=True,null=True)
    post_format = models.CharField(max_length=20, blank=True,null=True)
    durationMs = models.IntegerField(default=0)
    frameRate = models.IntegerField(default=0)
    category = models.CharField(max_length=20, blank=True,null=True)
    frameCount = models.IntegerField(default=0)
    fileSize = models.IntegerField(default=0)


@receiver(post_save, sender=FileUpload, dispatch_uid="insert-hashtag")
def update_hashtag(sender, instance,created, **kwargs):
    if instance.hashtag and created:
        data_tag = instance.hashtag
        data_tag = data_tag.split(",")
        for data in data_tag:
            try:
                try:
                    obj = HashTag.objects.get(hashtag=data)
                    if obj:
                        obj.count+=1
                        obj.save()
                except:
                    hash = HashTag(hashtag=data)
                    hash.save()
            except Exception as e:
                pass

@receiver(post_save, sender=FileUpload, dispatch_uid="insert-count")
def update_postcount(sender, instance,created,**kwargs):
    if created:
        objProfile = PhoneNumber.objects.get(user=instance.owner_id)
        objProfile.postCount+=1
        objProfile.save()



@receiver(post_delete, sender=FileUpload, dispatch_uid="delete_count")
def delete_postCount(sender, instance, **kwargs):
    objProfile = PhoneNumber.objects.get(user=instance.owner_id)
    
    objProfile.postCount-=1
    objProfile.save()
    

class FrameId(models.Model):
    frameId = models.IntegerField(default=0)
    frameCount = models.IntegerField(default=0)
    user = models.ForeignKey(User,on_delete=models.PROTECT,null=False,related_name='userIdFrame')

    # class Meta:
    #     unique_together = ('user', 'frameId')


@receiver(post_save, sender=FileUpload, dispatch_uid="insert-count-sticker")
def update_frame(sender, instance,created,**kwargs):
    if created:
        if instance.frameId:
            frameTag = instance.frameId
            frameTag = frameTag.split(",")
            for data in frameTag:
                try:
                    try:
                        obj = FrameId.objects.get(frameId=data)
                        if obj:
                            obj.frameCount+=1
                            obj.save()
                    except Exception as e:
                        obj = FrameId(frameId=data,user=instance.owner)
                        obj.save()
                        obj = FrameId.objects.get(frameId=data)
                        obj.frameCount+=1
                        obj.save()

                except Exception as e:
                    print(e)
                    pass
        

class StickerId(models.Model):
    postId = models.ForeignKey(FileUpload,on_delete=models.CASCADE,null=False,related_name='postSticker')
    stickerId = models.IntegerField(default=0)
    stickerCount = models.IntegerField(default=0)
    user = models.ForeignKey(User,on_delete=models.PROTECT,null=False,related_name='userIdSticker')

    

@receiver(post_save, sender=FileUpload, dispatch_uid="insert-count-sticker")
def update_sticker(sender, instance,created,**kwargs):
    if created:
        if instance.stickerId:
            frameTag = instance.frameId
            frameTag = frameTag.split(",")
            for data in frameTag:
                try:
                    try:
                        obj = StickerId.objects.get(stickerId=data)
                        if obj:
                            obj.stickerCount+=1
                            obj.save()
                    except Exception as e:
                        obj = StickerId(stickerId=data,user=instance.owner)
                        obj.save()
                        obj = StickerId.objects.get(stickerId=data)
                        obj.stickerCount+=1
                        obj.save()
                except Exception as e:
                    print(e)
                    pass

class PostLike(models.Model):
    postId = models.ForeignKey(FileUpload,on_delete=models.CASCADE,null=False,related_name='post')
    user = models.ForeignKey(User,on_delete=models.PROTECT,null=False,related_name='user')
    like = models.SmallIntegerField(default=0,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)


    class Meta:
        unique_together = ('postId', 'user','like')

    def __str__(self):
        return '%s-%s' % (self.user_id,self.postId_id)

@receiver(post_save, sender=PostLike, dispatch_uid="increment_like_count")
def update_like_count(sender, instance, **kwargs):
    if instance.like==1:
        instance.postId.likeCount+=1
        instance.postId.save()
        postData = instance.postId

        
        if postData.likeCount in [3,10,16,40,52,61,72,85,95,100]:
            notificationType = "PostLike"
            notificationMessage = instance.user.username +" and "+str(postData.likeCount-1)+" others Liked your Post"
            try:
                Notification.objects.filter(postId=postData.id,types=notificationType).delete()
            except Notification.DoesNotExist:
                pass    
            Notification.objects.create(toId=postData.owner,postId=postData,types=notificationType,message=notificationMessage)
            token=FirebaseNotification.objects.get(user=postData.owner)
            registration_token = token.token
            thumbnail = str(postData.thumbnail)
            hasThumbnail = thumbnail is not None and thumbnail is not ""
            short_link = utils.get_short_link("/post_update/"+postData.owner.username+"/"+str(postData.id))
            title = 'Congratulations!'
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=notificationMessage,
                ),
                data={
                    'title':title,
                    'message': notificationMessage,
                    'shortLink':short_link,
                    'types':notificationType,
                    'thumbnail':STORAGE_URL+"upload_thumbnail/"+thumbnail if hasThumbnail else "",
                },
                token=registration_token,   
            )
            response = messaging.send(message)

@receiver(post_delete, sender=PostLike, dispatch_uid="decrement_like_count")
def delete_count(sender, instance, **kwargs):
    if instance.postId.likeCount > 0:
        instance.postId.likeCount-=1
        instance.postId.save()        


class SavedPost(models.Model):
    postId = models.ForeignKey(FileUpload,on_delete=models.CASCADE,null=False,related_name='postsave')
    user = models.ForeignKey(User,on_delete=models.PROTECT,null=False,related_name='usersave')
    like = models.SmallIntegerField(default=0,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)

    class Meta:
        unique_together = ('postId', 'user')
    def __str__(self):
        return '%s-%s' % (self.user_id,self.postId_id)

class HashTag(models.Model):
    hashtag = models.CharField(default="",null=True,max_length=20,unique=True)
    count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)

    def __str__(self):
        return '%s' % (self.hashtag)


class ViewModel(models.Model):
    postId = models.ForeignKey(FileUpload,on_delete=models.CASCADE,null=False,related_name='postId')
    count = models.IntegerField(default=0)

@receiver(post_save, sender=ViewModel, dispatch_uid="increment_view_count")
def update_view_count(sender, instance, **kwargs):    
    instance.postId.viewCount+=1
    instance.postId.save()    

class FollowerModel(models.Model):
    followerId = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name='followerId')
    followingId = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name='followingId')
    follow = models.SmallIntegerField(default=0,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)

    class Meta:
        unique_together = ('followerId', 'followingId')

@receiver(post_save, sender=FollowerModel, dispatch_uid="update-follower")
def update_follower(sender, instance, **kwargs):
    userObjectFollow = PhoneNumber.objects.get(user_id=instance.followerId)
    userObjectFollow.followingCount+=1
    userObjectFollow.save()

@receiver(post_save, sender=FollowerModel, dispatch_uid="update-following")
def update_following(sender, instance, **kwargs):
    userObjectFollowing = PhoneNumber.objects.get(user_id=instance.followingId)
    userObjectFollowing.followerCount+=1
    userObjectFollowing.save()

@receiver(post_delete, sender=FollowerModel, dispatch_uid="update-followerq")
def unfollow_follower(sender, instance, **kwargs):
    userObjectFollow = PhoneNumber.objects.get(user_id=instance.followerId)    
    userObjectFollowing = PhoneNumber.objects.get(user_id=instance.followingId)
    if userObjectFollow.followingCount > 0:
        userObjectFollow.followingCount-=1
        userObjectFollow.save()
    if userObjectFollowing.followerCount > 0:
        userObjectFollowing.followerCount-=1
        userObjectFollowing.save()    
    
class FirebaseNotification(models.Model):
    user = models.ForeignKey(User,on_delete=models.PROTECT,null=True,related_name='user_fcm')
    token = models.CharField(default="",null=True,max_length=200,unique=False)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)

@receiver(post_save, sender=FollowerModel, dispatch_uid="notification")
def updateFollowNotifcation(sender, instance,created,**kwargs):
    user_id = User.objects.get(id=instance.followerId.id)
    reciever_id = User.objects.get(id=instance.followingId.id)
    notificationType = "Follow"
    notificationMessage = instance.followerId.username+" started Following You"
    title = "New Follower"
    if created:
        try: 
            Notification.objects.filter(fromId=user_id,types=notificationType).delete()
        except Notification.DoesNotExist:
            pass        
        
        Notification.objects.create(fromId=user_id,toId=reciever_id,fromUsername=user_id,types=notificationType,message=notificationMessage)
        token=FirebaseNotification.objects.get(user=reciever_id)
        registration_token = token.token
        profile_pic=PhoneNumber.objects.get(user_id=user_id)
        profilePic = str(profile_pic.profilePic)
        hasProfilePic = profilePic is not None and profilePic is not ""
        message = messaging.Message(
            notification=messaging.Notification(
                    title=title,
                    body=notificationMessage,
                ),
            data={
                'title':title,
                'message': notificationMessage,
                'fromId': str(user_id),
                'toId':str(reciever_id),
                'types':notificationType,
                'thumbnail':STORAGE_URL+"profile_dp/"+profilePic if hasProfilePic else "",
                'username':profile_pic.user.username,
                'fullName':profile_pic.fullName,
                'userId':str(profile_pic.user.id),
                'elevation':str(profile_pic.elevation)
            },
            token=registration_token,   
        )
        response = messaging.send(message)

class CommentModel(models.Model):
    postId = models.ForeignKey(FileUpload,on_delete=models.CASCADE,null=False,related_name='piD')
    userId = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name='userId')
    comment= models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    profId = models.ForeignKey(PhoneNumber,on_delete=models.CASCADE,null=False,related_name='profileId')
    likeCount = models.IntegerField(default=0)

class ReplyModel(models.Model):
    commentId = models.ForeignKey(CommentModel,on_delete=models.CASCADE,null=False,related_name='replies')
    reply = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    userId = models.ForeignKey(User,on_delete=models.CASCADE,null=False,related_name='Uid')
    profId = models.ForeignKey(PhoneNumber,on_delete=models.CASCADE,null=False,related_name='profileIdreply')
    likeCount = models.IntegerField(default=0)

    def __str__(self):
        return '%s' % (self.id)

class CommentLike(models.Model):
    commentId = models.ForeignKey(CommentModel,on_delete=models.CASCADE,null=False,related_name='commentLike')
    user = models.ForeignKey(User,on_delete=models.PROTECT,null=False,related_name='user_comment')
    like = models.SmallIntegerField(default=0,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    profId = models.ForeignKey(PhoneNumber,on_delete=models.PROTECT,null=False,related_name='profileIdCommentLike')


    class Meta:
        unique_together = ('commentId', 'user')
    def __str__(self):
        return '%s-%s' % (self.user_id,self.commentId_id)

@receiver(post_save, sender=CommentModel, dispatch_uid="update-commentcount")
def update_comment(sender, instance,created, **kwargs):
    if created:
        objPost = FileUpload.objects.get(id=instance.postId_id)
        print(objPost)
        objPost.commentCount+=1
        objPost.save()

@receiver(post_delete, sender=CommentModel, dispatch_uid="update-commentcount")
def decrement_comment(sender, instance, **kwargs):
    
    objPost = FileUpload.objects.get(id=instance.postId_id)
    if objPost.commentCount>0:
        objPost.commentCount-=1
        objPost.save()

@receiver(post_save, sender=CommentLike, dispatch_uid="update-commentcount")
def update_commentCount(sender, instance,created, **kwargs):
    if created:
        print("r-------------------------------------")
        objPost = CommentModel.objects.get(id=instance.commentId_id)
        print(objPost)
        objPost.likeCount+=1
        objPost.save()


@receiver(post_delete, sender=CommentLike, dispatch_uid="update-commentcount")
def decrement_commentCount(sender, instance, **kwargs):
    print("r-------------------------------------")
    objPost = CommentModel.objects.get(id=instance.commentId_id)
    if objPost.likeCount>0:
        objPost.likeCount-=1
        objPost.save()




class ReplyLike(models.Model):
    replyId = models.ForeignKey(ReplyModel,on_delete=models.CASCADE,null=True,related_name='replyLike')
    user = models.ForeignKey(User,on_delete=models.PROTECT,null=True,related_name='user_reply')
    like = models.SmallIntegerField(default=0,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    profId = models.ForeignKey(PhoneNumber,on_delete=models.PROTECT,null=False,related_name='profileIdreplyLike')


    class Meta:
        unique_together = ('replyId', 'user')
    def __str__(self):
        return '%s-%s' % (self.user_id,self.replyId)
# @receiver(post_save, sender=CommentModel, dispatch_uid="update-commentcount")
# def update_reply_countLike(sender, instance, **kwargs):
#     print(instance.postId)
#     objPost = FileUpload.objects.get(id=instance.postId_id)
#     print(objPost)
#     objPost.commentCount+=1
#     objPost.save()
@receiver(post_save, sender=ReplyLike, dispatch_uid="update-replycount")
def update_replyCount(sender, instance,created, **kwargs):
    if created:
        objPost = ReplyModel.objects.get(id=instance.replyId_id)
        
        objPost.likeCount+=1
        objPost.save()

@receiver(post_delete, sender=ReplyLike, dispatch_uid="update-replycount")
def decrement_replyCount(sender, instance, **kwargs):
    
    objPost = ReplyModel.objects.get(id=instance.replyId_id)
    if objPost.likeCount>0:
        objPost.likeCount-=1
        objPost.save()



