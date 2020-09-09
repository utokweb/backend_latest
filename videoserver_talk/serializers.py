from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.authtoken.models import Token
import requests
import math, random 
from .models import PhoneNumber,FileUpload,PostLike,ViewModel,HashTag,FollowerModel,CommentModel,ReplyModel,CommentLike,ReplyLike
from rest_framework.fields import ListField


API_URL = "http://18.220.150.215:8000"

# class StringArrayField(ListField):
#     """
#     String representation of an array field.
#     """
#     def to_representation(self, obj):
#         print(obj)
#         print("dssdfgdfgdgfgdfgdfhgdfgdfgdfgdfgsdgsdfasgasdgad")
#         obj = super().to_representation(obj)
#         # convert list to string
#         return ",".join([str(element) for element in obj])

#     def to_internal_value(self, data):
#         print(data)
#         data = data.split(",")  # convert string to list
#         return super().to_internal_value(self, data)

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    username = serializers.CharField(
            max_length=32,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
            
    password = serializers.CharField(min_length=8,write_only=True)
    

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'],
             validated_data['password'])
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

class UserLoginSerializer(serializers.ModelSerializer):
    
    username = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        write_only=True,
        label="Email Address"
    )

    token = serializers.CharField(
        allow_blank=True,
        read_only=True
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta(object):
        model = User
        fields = ['email', 'username', 'password', 'token']

    def validate(self, data):
        email = data.get('email', None)
        username = data.get('username', None)
        password = data.get('password', None)

        if not email and not username:
            raise serializers.ValidationError("Please enter username or email to login.")

        user = User.objects.filter(
            Q(email=email) | Q(username=username)
        ).exclude(
            email__isnull=True
        ).exclude(
            email__iexact=''
        ).distinct()

        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise serializers.ValidationError("This username/email is not valid.")

        if user_obj:
            if not user_obj.check_password(password):
                raise serializers.ValidationError("Invalid credentials.")

        if user_obj.is_active:
            token, created = Token.objects.get_or_create(user=user_obj)
            data['token'] = token
            data['user'] = user_obj
            #update_password(email,password)
        else:
            raise serializers.ValidationError("User not active.")
        
        return data

class FullNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = ['id','phone_number','bio','fullName','profilePic','followerCount','followingCount','postCount']

class ProfileSerializer2(serializers.ModelSerializer):
    user = FullNameSerializer(many=False, read_only=True)
    class Meta:
        model = PhoneNumber
        fields = ['id','fullName','profilePic','followerCount','followingCount','user','postCount']

# class Base64ImageField(serializers.ImageField):
    
#     def to_internal_value(self, data):
#         from django.core.files.base import ContentFile
#         import base64
#         import six
#         import uuid
#         import json

#         if isinstance(data, six.string_types):x 
#             data = json.dumps(data)
#             print(data)
#             data = base64.b64encode(data.encode('utf-8'))
#             print(data)
#             data = json.loads(data)
#             if 'data:' in data and ';base64,' in data:
#                 header, data = data.split(';base64,')

#             try:
#                 decoded_file = base64.b64decode(data)
#             except TypeError:
#                 self.fail('invalid_image')

#             file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
#             file_extension = self.get_file_extension(file_name, decoded_file)
#             complete_file_name = "%s.%s" % (file_name, file_extension, )
#             data = ContentFile(decoded_file, name=complete_file_name)

#         return super(Base64ImageField, self).to_internal_value(data)

#     def get_file_extension(self, file_name, decoded_file):
#         import imghdr

#         extension = imghdr.what(file_name, decoded_file)
#         extension = "jpg" if extension == "jpeg" else extension

#         return extension

class FileUploadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FileUpload
        fields = ['id','created', 'datafile', 'owner','description','privacy','thumbnail','likeCount','viewCount','hashtag','commentCount']    
    
class FileUploadSerializer2(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
     )
    
     
    
    class Meta:
        model = FileUpload
        fields = ['id','created', 'datafile', 'owner','description','privacy','thumbnail','likeCount','viewCount','hashtag','commentCount']

  



class UserSearchSerializer(serializers.ModelSerializer):
    user = FullNameSerializer(many=False, read_only=True)
    # user = serializers.SlugRelatedField(
    #     many=False,
    #     read_only=True,
    #     slug_field=('username')
    #  )
    class Meta:
        model = PhoneNumber
        fields = ['fullName','user','profilePic']

class PostLikeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PostLike
        fields=['like','postId','user']

class PostLikeSerializer2(serializers.ModelSerializer):
    
    class Meta:
        model = PostLike
        fields=['postId']

class ViewSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewModel
        fields=['postId','count']

class HashtagSearchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = HashTag
        fields = ['hashtag','count']

class HashtagSearchSerializer2(serializers.ModelSerializer):
    
    class Meta:
        model = HashTag
        fields = ['hashtag']

class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowerModel
        fields = ['followerId','followingId']

# class ProfileSerializer3(serializers.ModelSerializer):
#     class Meta:
#         model = PhoneNumber
#         fields = ['profilePic']


class ProfileSerializer3(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = ['fullName','profilePic']


class ReplySerializer(serializers.ModelSerializer):
    userId = FullNameSerializer(many=False, read_only=True)
    profId = ProfileSerializer3(many=False,read_only=True)

    class Meta:
        model = ReplyModel
        fields = ['id','commentId','reply','userId','profId','likeCount','created']

class ReplySerializer2(serializers.ModelSerializer):
    

    class Meta:
        model = ReplyModel
        fields = ['id','commentId','reply','userId','profId']

class CommentSerializer2(serializers.ModelSerializer):
    userId = FullNameSerializer(many=False, read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    profId = ProfileSerializer3(many=False,read_only=True)
    
    class Meta:
        model = CommentModel
        fields = ['id','postId','userId','comment','created','replies','profId','likeCount']

class CommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CommentModel
        fields = ['id','postId','userId','comment','profId']

class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['commentId','user','like','profId']

class CommentLikeSerializer2(serializers.ModelSerializer):
    user = FullNameSerializer(many=False, read_only=True)
    profId = ProfileSerializer3(many=False,read_only=True)
    class Meta:
        model = CommentLike
        fields = ['id','commentId','user','like','profId']

class ReplyLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplyLike
        fields = ['id','replyId','user','like','profId']

class ReplyLikeSerializer2(serializers.ModelSerializer):
    user = FullNameSerializer(many=False, read_only=True)
    profId = ProfileSerializer3(many=False,read_only=True)
    class Meta:
        model = ReplyLike
        fields = ['id','replyId','user','like','profId']