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
from youtalk.storage_backends import PublicMediaStorage,PrivateMediaStorage

def user_directory_path_profile(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'profile_{0}/{1}'.format(instance.user.id, instance.user.username)
class PhoneNumber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=500, blank=True,null=True,unique=True)
    bio = models.TextField(blank=True)
    fullName = models.CharField(max_length=20, blank=True,null=False)
    profilePic = models.ImageField(storage=PublicMediaStorage(),default="")
    followerCount = models.IntegerField(default=0,blank=True)
    followingCount = models.IntegerField(default=0,blank=True)
    postCount = models.IntegerField(default=0,blank=True)
    
    #birthdDate = models.DateField(auto_created = True,blank=True)

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.owner.id, filename)
class FileUpload(models.Model):
    privacy_choices = (
        ('only_me', 'Only Me'),
        ('private', 'Private'),
        ('public', 'Public'),
    )
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, to_field='id',on_delete=models.CASCADE)
    datafile = models.FileField(storage=PublicMediaStorage())
    thumbnail = models.ImageField(storage=PublicMediaStorage(),default="")
    description = models.TextField(blank=True)
    privacy = models.CharField(max_length=20,choices=privacy_choices,default="public")
    likeCount = models.IntegerField(default=0)
    viewCount = models.IntegerField(default=0)
    hashtag = models.TextField(max_length=10001, blank=True)
    commentCount = models.IntegerField(default=0)
        

@receiver(post_save, sender=FileUpload, dispatch_uid="insert-hashtag")
def update_hashtag(sender, instance, **kwargs):
    if instance.hashtag:
        data_tag = instance.hashtag
        data_tag = data_tag.split(",")
        for data in data_tag:
            try:
                try:
                    obj = HashTag.objects.get(hashtag=data)
                    if obj:
                        obj.count+=1
                        obj.save()
                except Exception as e:
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
    
                
        


class PostLike(models.Model):
    postId = models.ForeignKey(FileUpload,on_delete=models.CASCADE,null=False,related_name='post')
    user = models.ForeignKey(User,on_delete=models.PROTECT,null=False,related_name='user')
    like = models.SmallIntegerField(default=0,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)


    class Meta:
        unique_together = ('postId', 'user','like')
    def __str__(self):
        return '%s-%s' % (self.user_id,self.postId_id)


class HashTag(models.Model):
    hashtag = models.CharField(default="",null=True,max_length=20,unique=True)
    count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)



    def __str__(self):
        return '%s' % (self.hashtag)



@receiver(post_save, sender=PostLike, dispatch_uid="increment_like_count")
def update_count(sender, instance, **kwargs):
    if instance.like==1:
        instance.postId.likeCount+=1
        instance.postId.save()
    else:
        instance.postId.likeCount-=1

@receiver(post_delete, sender=PostLike, dispatch_uid="decrement_like_count")
def delete_count(sender, instance, **kwargs):
    instance.postId.likeCount-=1
    instance.postId.save()

class ViewModel(models.Model):
    postId = models.ForeignKey(FileUpload,on_delete=models.CASCADE,null=False,related_name='postId')
    count = models.IntegerField(default=0)

@receiver(post_save, sender=ViewModel, dispatch_uid="increment_view_count")
def update_count(sender, instance, **kwargs):
    
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
    
    userObjectFollow.followingCount-=1
    userObjectFollow.save()
    

@receiver(post_delete, sender=FollowerModel, dispatch_uid="update-followingId")
def unfollow_follower(sender, instance, **kwargs):
    userObjectFollowing = PhoneNumber.objects.get(user_id=instance.followingId)
    userObjectFollowing.followerCount-=1
    userObjectFollowing.save()

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
    commentId = models.ForeignKey(CommentModel,on_delete=models.PROTECT,null=False,related_name='commentLike')
    user = models.ForeignKey(User,on_delete=models.PROTECT,null=False,related_name='user_comment')
    like = models.SmallIntegerField(default=0,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    profId = models.ForeignKey(PhoneNumber,on_delete=models.PROTECT,null=False,related_name='profileIdCommentLike')


    class Meta:
        unique_together = ('commentId', 'user')
    def __str__(self):
        return '%s-%s' % (self.user_id,self.commentId_id)

@receiver(post_save, sender=CommentModel, dispatch_uid="update-commentcount")
def update_comment(sender, instance, **kwargs):
    print(instance.postId)
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
def update_commentCount(sender, instance, **kwargs):
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
    replyId = models.ForeignKey(ReplyModel,on_delete=models.PROTECT,null=False,related_name='replyLike')
    user = models.ForeignKey(User,on_delete=models.PROTECT,null=False,related_name='user_reply')
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
def update_replyCount(sender, instance, **kwargs):
    
    objPost = ReplyModel.objects.get(id=instance.replyId_id)
    
    objPost.likeCount+=1
    objPost.save()

@receiver(post_delete, sender=ReplyLike, dispatch_uid="update-replycount")
def decrement_replyCount(sender, instance, **kwargs):
    
    objPost = ReplyModel.objects.get(id=instance.replyId_id)
    if objPost.likeCount>0:
        objPost.likeCount-=1
        objPost.save()