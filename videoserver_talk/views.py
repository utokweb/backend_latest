from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # <-- Here
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from videoserver_talk.serializers import UserSerializer,UserLoginSerializer,MusicSerializer,ProfileSerializer,FileUploadSerializer,FileUploadSerializer2,UserSearchSerializer,PostLikeSerializer,PostLikeSerializer2,ViewSetSerializer,HashtagSearchSerializer,FollowerSerializer,ProfileSerializer2,CommentSerializer,ReplySerializer,HashtagSearchSerializer2,CommentSerializer2,ReplySerializer2,CommentLikeSerializer,CommentLikeSerializer2,ReplyLikeSerializer,ReplyLikeSerializer2,PostsaveSerializer2,PostsaveSerializer,TestPostSerializer,NotificationSerializer,FirebaseNotificationSerializer,BlockRequestSerializer,PostReportSerializer,OriginalAudioPostSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import requests
from rest_framework.parsers import FormParser, MultiPartParser
import sys
from rest_framework.pagination import PageNumberPagination
import django_filters
from .models import PhoneNumber,FileUpload,MusicTracks,PostLike,HashTag,FollowerModel,CommentModel,ReplyModel,CommentLike,ReplyLike,SavedPost,PostUploadTest,FrameId,StickerId,Notification,FirebaseNotification,BlockRequest,PostReportRequest,OriginalAudioPost
import json
from django.http import Http404
from rest_framework import status
import math,random
from rest_framework.decorators import api_view
from django.forms.models import model_to_dict
from django.db.models import Q
from rest_framework import mixins
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import ParseError
from django.db.models import Max
from rest_framework.parsers import FileUploadParser
from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from .pagination import CustomPagination,CustomPagination2,CustomPagination3
from youtalk.storage_backends import STORAGE_URL
import datetime,pytz

VERSION = 13 #Refers to Application Version Code
VERSION_STRING = "1.1.2"
STRICT = False #If True, Application won't proceed without user Updating the Application to Latest Build


@api_view(['GET'])
def checkApplicationVersion(request):
    return Response({
        "version_code":VERSION,
        "version_string":VERSION_STRING,
        "strict":STRICT
    })
        


class HelloView(APIView):
    permission_classes = (IsAuthenticated,) 

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

class UserCreate(APIView):
    """ 
    Creates the user. 
    """
    

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                PhoneNumber.objects.create(user=user,phone_number=request.data['phone_number'],fullName=request.data['full_name'])
        
                token = Token.objects.create(user=user)
                json_res = serializer.data
                json_res['token'] = token.key
                user = User.objects.get(id=json_res['id'])
                try:
                    FirebaseNotification.objects.get(user=user)
                except Exception as identifier:
                    FirebaseNotification.objects.create(user=user)

                return Response(json_res, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BlockRequests(APIView):
    
    def get(self, request,pk, format=None):
        blockedUsers = BlockRequest.objects.filter(blockedBy=pk)
        serializer = BlockRequestSerializer(blockedUsers, many=True)
        print(serializer.data)
        for f in serializer.data:
            profile_pic=PhoneNumber.objects.get(user=f['blockedUser'])
            profilePic = str(profile_pic.profilePic)
            if profilePic=="":
                f.update({"profilePic":None,"userame":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id,"elevation":profile_pic.elevation})
            else:
                #chnage by nitesh
                f.update({"profilePic":STORAGE_URL+"profile_dp/"+profilePic,"username":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id,"elevation":profile_pic.elevation})        
        return Response(serializer.data)        

    def post(self, request, format=None):
        print(request.data)
        serializer = BlockRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            blockedBy = request.data['blockedBy']
            blockedUser = request.data['blockedUser']
            try:
                #Removing Following Status for Both Users
                FollowerModel.objects.filter(followerId=blockedBy,followingId=blockedUser).delete()
                FollowerModel.objects.filter(followerId=blockedUser,followingId=blockedBy).delete()
            except:
                pass
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self,pk):
        return BlockRequest.objects.filter(id=pk)

    def delete(self, request,pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)        
            

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000
    
class UserLoginAPIView(APIView):
    """
    Endpoint for user login. Returns authentication token on success.
    """

    permission_classes = (permissions.AllowAny, )
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            userResp = serializer.data
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# {
# "username":"8872750000",
# "password":"Rahul17@@@",
# "email":"utalk@gmaail.com",
# "full_name":"rsethi"
# }

@api_view(['GET', 'POST','OPTIONS'])
def generateOTP(request) : 
  
    # Declare a digits variable   
    # which stores all digits  
    digits = "0123456789"
    OTP = "" 
  
   # length of password can be chaged 
   # by changing value in range 
    for i in range(4) : 
        OTP += digits[math.floor(random.random() * 10)] 
  
    return Response({"OTP":OTP})

@api_view(['GET', 'POST','OPTIONS'])
def check_phone_number(request):
    mobile_no = request.GET['phone_number']
    try:
        user = PhoneNumber.objects.get(phone_number=mobile_no)
        token = Token.objects.get(user=user.user)
    except:
        user = None
        return Response({"user":user})
    try:
        FirebaseNotification.objects.get(user=user.user)
    except:
        FirebaseNotification.objects.create(user=user.user)
    return Response({"user":model_to_dict(user.user),"token":model_to_dict(token)})

@api_view(['GET', 'POST','OPTIONS'])
def check_username(request):
    
    username = request.GET['username']
    try:
        user = User.objects.get(username=username)
        
        #token = Token.objects.get(user=user)
        user = True
        #print(token)
    except Exception as identifier:
        user = False
        return Response({"user":user})
    return Response({"user":user})


class UserProfile(APIView):
    #permission_classes = (IsAuthenticated,)
    def get_object(self, user):
        try:
            profile_id = PhoneNumber.objects.get(user_id=user.id)
            return profile_id    
        except PhoneNumber.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        if isinstance(pk, int):
            user = User.objects.get(id=pk)
        else:
            user = User.objects.get(username=pk)
        profile = self.get_object(user)
        serializer = ProfileSerializer(profile)
        return Response({"user_profile":serializer.data,"user_data":model_to_dict(user)})

    def put(self, request, pk, format=None):
        if isinstance(pk, int):
            user = User.objects.get(id=pk)
        else:
            user = User.objects.get(username=pk)
        profile = self.get_object(user)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileUploadViewSet(APIView):
    #permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser,)

    def post(self, request, *args, **kwargs):
        fileSerializer = FileUploadSerializer(data=request.data)
        if fileSerializer.is_valid():
            fileSerializer.save()
            res = dict(fileSerializer.data)
            username = User.objects.get(id=res['owner'])
            serialize_data = fileSerializer.data
        
            try:
                music = MusicTracks.objects.filter(id=serialize_data['musicTrack']).values()
                serialize_data.update({"musicTrack":music[0]})
            except Exception as identifier:
                pass
            serialize_data.update({"owner":username.username})

            #Adding an OriginialAudioPost entry ( if Applicable )
            try:
                originalPost = request.data['originalAudioSource']
                if originalPost is not None:
                    usingPostOwner = request.data['owner']
                    usingPost = serialize_data['id']
                    originalAudioSerializer = OriginalAudioPostSerializer(data={'originalPost':originalPost,'usingPost':usingPost,'usingPostOwner':usingPostOwner})
                    if originalAudioSerializer.is_valid():
                        originalAudioSerializer.save()
                        originalPostData = FileUpload.objects.get(id=originalPost)
                        originalPostData.originalAudioUsage += 1
                        originalPostData.save()
                    else:
                        print(originalAudioSerializer.errors)    
            except Exception as e:
                print(e)
                pass                                    

            return Response(serialize_data, status=status.HTTP_201_CREATED)
        return Response(fileSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class OriginalAudioPostView(APIView,CustomPagination2):
    def get(self,request,pk):
        try:
            originalAudioPosts = OriginalAudioPost.objects.filter(originalPost__id=pk).order_by('-created')
            results = self.paginate_queryset(originalAudioPosts, request, view=self)
            serializer = OriginalAudioPostSerializer(results,many=True)
            for post in serializer.data:
                postData = FileUpload.objects.get(id=post['usingPost'])
                postSerializer = FileUploadSerializer2(postData)
                post.update({"usingPost":postSerializer.data})
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            print(e)    
        return Response({"results":[],"count":0})

    def post(self,request):
        serializerData = OriginalAudioPostSerializer(data=request.data)       
        if serializerData.is_valid():
            serializerData.save()
            return Response({"status":0,"data":serializerData.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status":1,"errors":serializerData.errors}, status=status.HTTP_400_BAD_REQUEST)        


        
class ReportPostViewSet(APIView):

    def get(self,request,pk):
        reportedPosts = PostReportRequest.objects.filter(reportedBy=pk)
        serializer = PostReportSerializer(reportedPosts,many=True)
        return Response(serializer.data)

    def post(self,request,*args,**kwargs):
        reportSerializer = PostReportSerializer(data=request.data)

        if(reportSerializer.is_valid()):
            reportSerializer.save()
            return Response(reportSerializer.data, status=status.HTTP_201_CREATED)

        return Response(reportSerializer.errors, status=status.HTTP_400_BAD_REQUEST)        



class TestUserUpload(APIView):
    #permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser,)

    def get(self, request, *args, **kwargs):
        category = request.GET['category']
        post = PostUploadTest.objects.filter(category=category)
        fileSerializer = TestPostSerializer(post,many=True)
        return Response(fileSerializer.data, status=status.HTTP_201_CREATED)
        

    def post(self, request, *args, **kwargs):
        fileSerializer = TestPostSerializer(data=request.data)
        
        if fileSerializer.is_valid():
            fileSerializer.save()
            # res = dict(fileSerializer.data)
            # username = User.objects.get(id=res['owner'])
            serialize_data = fileSerializer.data
            # serialize_data.update({"owner":username.username})
            return Response(serialize_data, status=status.HTTP_201_CREATED)
        print(fileSerializer.errors)
        return Response(fileSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationViewSet(APIView,CustomPagination3):
    def get_object(self,pk):
        return Notification.objects.filter(toId=pk).order_by('-created')
    
    def get(self, request, pk, format=None):
        notification = self.get_object(pk)
        results = self.paginate_queryset(notification, request, view=self)
        serializer = NotificationSerializer(results,many=True)
        for f in serializer.data:
            
            profile_pic=PhoneNumber.objects.get(user_id=f['fromId'])
            profilePic = str(profile_pic.profilePic)
            print(profilePic)
            
            if profilePic=="":
                print("fdfdfdf")
                f.update({"profilePic":None,"username":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id,"elevation":profile_pic.elevation})
            else:
                f.update({"profilePic":STORAGE_URL+"profile_dp/"+profilePic,"username":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id,"elevation":profile_pic.elevation})
        

        return self.get_paginated_response(serializer.data)

class FollowerGetViewSet(APIView,CustomPagination3):
    def get_object(self,pk):
        
        return FollowerModel.objects.filter(followingId=pk)
        

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        results = self.paginate_queryset(post, request, view=self)
        serializer = FollowerSerializer(results,many=True)
        for f in serializer.data:
            
            profile_pic=PhoneNumber.objects.get(user=f['followerId'])
            profilePic = str(profile_pic.profilePic)
            print(profilePic)
            if profilePic=="":
                f.update({"profilePic":None,"userame":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id,"elevation":profile_pic.elevation})
            else:
                f.update({"profilePic":STORAGE_URL+"profile_dp/"+profilePic,"username":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id,"elevation":profile_pic.elevation})
        
        return self.get_paginated_response(serializer.data)
        
class FollowingGetViewSet(APIView,CustomPagination3):
    def get_object(self,pk):
        
        return FollowerModel.objects.filter(followerId_id=pk)
        

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        results = self.paginate_queryset(post, request, view=self)
        serializer = FollowerSerializer(results,many=True)
        #for f in serializer.data:
	#test
        for f in serializer.data:
            
            try:
                profile_pic=PhoneNumber.objects.get(user=f['followingId'])
                profilePic = str(profile_pic.profilePic)
                print(profilePic)
                if profilePic=="":
                    f.update({"profilePic":None,"username":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id,"elevation":profile_pic.elevation})
                else:
                    f.update({"profilePic":STORAGE_URL+"profile_dp/"+profilePic,"username":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id,"elevation":profile_pic.elevation})
            except PhoneNumber.DoesNotExist:
                pass

        return self.get_paginated_response(serializer.data)

class UserVideoViewSet(APIView,CustomPagination):
    #permission_classes = (IsAuthenticated,)
    # serializer_class = FileUploadSerializer2

    # def get_queryset(self):
    #     user_id = self.kwargs['pk']
    #     return FileUpload.objects.filter(owner_id=user_id)
    def get_object(self, pk):
        status_ = 2
        try:
            try:
                userId = self.request.GET['userId']
                status = FollowerModel.objects.filter(followerId=pk,followingId=userId)
                if status:
                    if int(userId)==int(pk):
                        status_ =2
                    else:
                        status_= 1
                else:
                    if int(userId)==int(pk):
                        status_ =2
                    else:
                        status_=0
            except:
                status_= 0

            if status_== 1:
                return FileUpload.objects.filter(Q(privacy="public") | Q(privacy="private"),owner_id=userId).order_by('-created')
            elif status_== 0:
                return FileUpload.objects.filter(privacy="public",owner_id=userId).order_by('-created')
            elif status_ == 2:
                return FileUpload.objects.filter(owner_id=userId).order_by('-created')

        except FileUpload.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        userId = self.request.GET['userId']
        user = User.objects.get(id=userId)
        profile_data=PhoneNumber.objects.get(user__id=user.id)
        upload = self.get_object(pk)
        results = self.paginate_queryset(upload, request, view=self)
        serializer = FileUploadSerializer2(results,many=True)
        for f in serializer.data:
            profilePic = str(profile_data.profilePic)
            if profilePic=="":
                f.update({"profilePic":STORAGE_URL+"profile_dp/"+profilePic,"user_id":user.id})
            else:
                f.update({"profilePic":None,"user_id":user.id})

        #pagination_class = StandardResultsSetPagination

        return self.get_paginated_response(serializer.data)


class EditUserUploads(APIView):

    def get_object(self, pk):
        return FileUpload.objects.get(id=pk)

    def put(self, request, pk, format=None):
        profile = self.get_object(pk)
        
        serializer = FileUploadSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Timeline(APIView,CustomPagination2):

    def get(self, request,pk, format=None):
        # In future we need to get the timezone from client side to query the
        # posts accordingly
        orderBy = ["viewCount"]
        now = datetime.datetime.now(tz=pytz.timezone("Asia/Kolkata"))
        if now.minute <20:
            if 21 <= now.hour <= 3:
                orderBy = ["profId__gender"]
            else:
                orderBy = ["-viewCount","-created"]
        elif 20<= now.minute <=40:
            if 12 <= now.hour <= 15:
                orderBy = ["created"]
            else:
                orderBy = ["-created"]

        fileupload = FileUpload.objects.filter(privacy="public",reportsCount__lt=5).order_by(*orderBy)
        if pk != None and pk > 0 :
            blockRequests = BlockRequest.objects.filter(blockedBy=pk)
            userIds = blockRequests.values_list('blockedUser',flat=True)
            # TO EXCLUDE REPORTED POSTS - NOT WORKING DUE TO MULTIPLE "IN" EXCLUDES
            # reportedPosts = PostReportRequest.objects.filter(reportedBy=pk)
            # reportedPostIds = reportedPosts.values_list('post',flat=True)
            fileupload = FileUpload.objects.filter(privacy="public",reportsCount__lt=5).order_by(*orderBy).exclude(owner_id__in=userIds)
        results = self.paginate_queryset(fileupload, request, view=self)
        serializer = FileUploadSerializer2(results, many=True)
        for f in serializer.data:    
            user_id = User.objects.get(username=f['owner'])
            profile_pic=PhoneNumber.objects.get(user=user_id)
            profilePic = str(profile_pic.profilePic)
            if profilePic=="":
        	    f.update({"profilePic":None,"user_id":user_id.id})
            else:
                f.update({"profilePic":STORAGE_URL+"profile_dp/"+profilePic,"user_id":user_id.id})
        return self.get_paginated_response(serializer.data)

class TimelineFollowing(APIView,CustomPagination2):
    def get(self, request, format=None):
        userId = self.request.GET['userId']
        fileupload = FileUpload.objects.filter(privacy="public").exclude(owner_id = int(userId)).order_by('-created')
        
        serializer = FileUploadSerializer2(fileupload, many=True)
        res = serializer.data
        result=[]
        for z in res:
            
            try:
                user_id = User.objects.get(username=z['owner'])
                pk = user_id.id
                print(pk)
                status = FollowerModel.objects.filter(followerId=userId,followingId=pk)
                
                
                if status:
                    if int(userId)==int(pk):
                        status_ = 2
                    else:
                        status_= 1
                else:
                    if int(userId)==int(pk):
                        status_ =2
                    else:
                        status_=0
            except Exception as e:
                status_= 0
            

            if status_==0:
                print(status_)
                del(z)
            else:
                user_id = User.objects.get(username=z['owner'])
                profile_pic=PhoneNumber.objects.get(user=user_id)
                profilePic = str(profile_pic.profilePic)
                if profilePic=="":
                    z.update({"profilePic":None,"user_id":user_id.id})
                else:
                    z.update({"profilePic":STORAGE_URL+"profile_dp/"+profilePic,"user_id":user_id.id})
                    
                result.append(z)
        results = self.paginate_queryset(result, request, view=self)
        return self.get_paginated_response(result)

class ProfileFilter(django_filters.FilterSet):
    username =  django_filters.CharFilter(name="user__username")
    class Meta:
        model = PhoneNumber
        fields = ['fullName', 'username']


class HashTagFilter(generics.ListCreateAPIView):
    queryset = HashTag.objects.all()
    serializer_class = HashtagSearchSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['hashtag']

class PostLikes(APIView):
    
    def get(self, request, format=None):
        postLike = PostLike.objects.filter(like=1)
        serializer = PostLikeSerializer(postLike, many=True)
        print(serializer.data)
        return Response(serializer.data)

    def post(self, request, format=None):
        print(request.data)
        serializer = PostLikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserSearch(generics.ListCreateAPIView):
    queryset = PhoneNumber.objects.all()
    serializer_class = UserSearchSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['fullName','user__username']

class UserPostLike(APIView):

    def get_object(self, pk):
        try:
            print(pk)
            return PostLike.objects.filter(user_id=pk,like=1)
        except PostLike.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        l = []
        post = self.get_object(pk)
        serializer = PostLikeSerializer2(post,many=True)
        for p in serializer.data:
            l.append(p['postId'])
        return Response(l)



class DeletePostAPIView(APIView):
    def get_object(self,pk):
        
        return FileUpload.objects.get(id=pk)

    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class UserPostLikeUpdate(APIView):
    def get_object(self,pk):
        
        return PostLike.objects.get(postId_id=pk,user_id=self.request.GET['user_id'])
        

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostLikeSerializer(post,many=False)
        return Response(serializer.data)
        
    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ViewSetApiView(APIView):
    def post(self, request, format=None):
        serializer = ViewSetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HashTagPostSearch(APIView):
    def get(self, request, format=None):
        l = []
        fileupload = FileUpload.objects.filter(privacy="public").values()
        search = request.GET['search']
        for f in fileupload:
            list_ = f['hashtag']
            list_1 = list_.split(",")
            try:
                for z in list_1:
                    if search == z:
                        dict_ = f
                        hashtag_count = HashTag.objects.get(hashtag=search)
                        username = User.objects.get(id=dict_['owner_id'])
                        elevation = PhoneNumber.objects.get(user=dict_['owner_id'])
                        profId = {"followerCount":elevation.followerCount,"followingCount":elevation.followingCount,"elevation":elevation.elevation}
                        dict_.update({"count":str(hashtag_count.count),"owner":username.username,"user_id":dict_['owner_id'],"code":search,"datafile":STORAGE_URL+"upload_vedio/"+dict_['datafile'],"thumbnail":STORAGE_URL+"upload_thumbnail/"+dict_['thumbnail'],"latitude":str(dict_['latitude']),"longitude":str(dict_['longitude']),'profId':profId})
                        l.append(dict_)         
            except Exception as identifier:
                pass
        return Response(l)

class FollowSetApiView(APIView):
    def post(self, request, format=None):
        serializer = FollowerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UnfollowApiSet(APIView):
    def get_object(self,pk):
        return FollowerModel.objects.filter(followerId_id=pk,followingId_id=self.request.GET['followingId'])

    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        print(post)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TopUserApiSet(APIView):
     
    def get(self, request, format=None):
        post = PhoneNumber.objects.all().order_by('-followerCount')[:5]
        print(post)
        serializer = ProfileSerializer2(post,many=True)
        print(serializer.data)
        return Response(serializer.data)

class MostCommonFrame(APIView):
    def get(self, request, format=None):
        post = FrameId.objects.all().values_list('frameId', flat=True).order_by('-frameCount')
        
        return Response(post)

class MostCommonSticker(APIView):
    def get(self, request, format=None):
        post = StickerId.objects.all().values_list('stickerId', flat=True).order_by('-stickerCount')
        
        return Response(post)
class TopTrendingPostApiSet(APIView):
     
    def get(self, request, format=None):
        post = FileUpload.objects.all().order_by('-viewCount')[:5]
        
        serializer = FileUploadSerializer2(post,many=True)
        for f in serializer.data:
                user_id = User.objects.get(username=f['owner'])
                profile_pic=PhoneNumber.objects.get(user=user_id)
                profilePic = str(profile_pic.profilePic)
                f.update({"profilePic":STORAGE_URL+"profile_dp/"+profilePic,"user_id":user_id.id})
        return Response(serializer.data)

class TopTrendingHashApiSet(APIView):
     
    def get(self, request, format=None):
        l= {}
        hashTag = HashTag.objects.all().order_by('-count')[:3]
        
        serializer = HashtagSearchSerializer2(hashTag,many=True)
        for hashtags in serializer.data:
            search = FileUpload.objects.filter(hashtag__contains=hashtags['hashtag']).order_by('-viewCount')[:3]
            serializer_data = FileUploadSerializer2(search,many=True)
            for f in serializer_data.data:
                user_id = User.objects.get(username=f['owner'])
                profile_pic=PhoneNumber.objects.get(user=user_id)
                profilePic = str(profile_pic.profilePic)
                f.update({"profilePic":STORAGE_URL+"profile_dp/"+profilePic,"user_id":user_id.id})
            dict_ = {hashtags['hashtag']:serializer_data.data}
            l.update(dict_)
        return Response(l)

class TopHashTagApiSet(APIView):
     
    def get(self, request, format=None):
        post = HashTag.objects.all().order_by('-count')[:10]
        serializer = HashtagSearchSerializer(post,many=True)
        print(serializer.data)
        return Response(serializer.data)

class CheckFollowingStatus(APIView):
    def get(self, request, format=None):
        userId = self.request.GET['userId']
        followingId = self.request.GET['followingId']
        print(userId)
        print(followingId)
        try:
            status_ = FollowerModel.objects.get(followerId=userId,followingId=followingId)
            status = {"status":1}
        except FollowerModel.DoesNotExist:
            status = {"status":0}
        if status['status']==0:
            try:
                status_ = FollowerModel.objects.get(followerId=followingId,followingId=userId)
                status = {"status":2}
            except FollowerModel.DoesNotExist:
                status = {"status":0}

        return Response(status)

class FollowingList(APIView):
    def get(self, request, format=None):
        l = []
        userId = self.request.GET['userId']
        try:
            userList=FollowerModel.objects.filter(followerId=userId).values()
            for f in userList:
                l.append(f['followingId_id'])
        except FollowerModel.DoesNotExist:
            pass

        return Response(l)

class GetCommentPost(APIView):
    def get_object(self,pk):
        
        return CommentModel.objects.filter(postId=pk).order_by('-id')
        

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = CommentSerializer2(post,many=True)
        return Response(serializer.data)

class GetReplyPost(APIView):
    def get_object(self,pk):
        
        return ReplyModel.objects.get(commentId=pk)
        

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = ReplySerializer(post,many=False)
        return Response(serializer.data)

class PostComment(APIView):
    def post(self, request, format=None):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReplyComment(APIView):
    def post(self, request, format=None):
        serializer = ReplySerializer2(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentLikeApiView(APIView):
    def post(self, request, format=None):
        serializer = CommentLikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentUnlikeApiView(APIView):
    def get_object(self,pk):
        userId = self.request.GET['userId']
        return CommentLike.objects.get(commentId=pk,user=userId)

    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GetCommentLikeUser(APIView):
    def get_object(self,pk):
        return CommentLike.objects.filter(commentId=pk)
    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = CommentLikeSerializer2(post,many=True)
        return Response(serializer.data)

class MostViewApiView(APIView):
    def get_object(self,pk):
        status_ = 2
        try:
            try:
                userId = self.request.GET['userId']
                status = FollowerModel.objects.filter(followerId=pk,followingId=userId)
                print(status)
                if status:
                    if int(userId)==int(pk):
                        status_ =2
                    else:
                        status_= 1
                else:
                    print("ssssssssssssssss")
                    if int(userId)==int(pk):
                        status_ =2
                    else:
                        status_=0
            except Exception as e:
                status_= 0
            
            if status_== 1:
                return FileUpload.objects.filter(Q(privacy="public") | Q(privacy="private"),owner_id=userId).order_by('-viewCount')[:15]
            elif status_== 0:
                return FileUpload.objects.filter(privacy="public",owner_id=userId).order_by('-viewCount')[:15]
            elif status_ == 2:
                return FileUpload.objects.filter(owner_id=userId).order_by('-viewCount')[:15]
        except FileUpload.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = FileUploadSerializer2(post,many=True)
        return Response(serializer.data)

class MostLikeApiView(APIView):
    def get_object(self,pk):
        status_ = 2
        try:
            try:
                userId = self.request.GET['userId']
                status = FollowerModel.objects.filter(followerId=pk,followingId=userId)
                print(status)
                if status:
                    if userId==pk:
                        status_ =2
                    else:

                        status_= 1
                else:
                    print("ssssssssssssssss")
                    if int(userId)==int(pk):
                        status_ =2
                    else:
                        status_=0
            except Exception as e:
                status_= 0
            print(status_)
            if status_== 1:
                return FileUpload.objects.filter(Q(privacy="public") | Q(privacy="private"),owner_id=userId).order_by('-likeCount')[:15]
            elif status_== 0:
                return FileUpload.objects.filter(privacy="public",owner_id=userId).order_by('-likeCount')[:15]
            elif status_ == 2:
                return FileUpload.objects.filter(owner_id=userId).order_by('-likeCount')[:15]
        except FileUpload.DoesNotExist:
            raise Http404
        
    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = FileUploadSerializer2(post,many=True)
        return Response(serializer.data)

class ReplyLikeApiView(APIView):
    def post(self, request, format=None):
        serializer = ReplyLikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostSaveInsert(APIView):
    def post(self, request, format=None):
        serializer = PostsaveSerializer2(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetPostSaveInsert(APIView):
    def get_object(self,pk):
        return  SavedPost.objects.filter(user=pk)
    def get(self, request, pk, format=None):
        l=[]
        post = self.get_object(pk)
        for z in post:
            response = FileUploadSerializer2(z.postId)
            l.append(response.data)
        
        return Response(l)

class GetPostSaveId(APIView):
    def get_object(self,pk):
        return  SavedPost.objects.filter(user=pk)
    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        l=[]
        serializer = PostsaveSerializer2(post,many=True)
        for o in serializer.data:
            l.append(o['postId'])
        return Response(l)

class ReplyUnlikeApiView(APIView):
    def get_object(self,pk):
        userId = self.request.GET['userId']
        return ReplyLike.objects.get(commentId=pk,user=userId)

    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GetReplyLikeUser(APIView):
    def get_object(self,pk):
        return ReplyLike.objects.filter(commentId=pk)
    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = ReplyLikeSerializer2(post,many=True)
        return Response(serializer.data)

class AllCommentLike(APIView):
    def get_object(self,pk):
        return CommentLike.objects.filter(user_id=pk)
    def get(self, request, pk, format=None):
        l = []
        post = self.get_object(pk)
        print(post)
        serializer = CommentLikeSerializer2(post,many=True)
        for r in serializer.data:
            l.append(r['commentId'])
        return Response(l)

class AllReplyLike(APIView):
    def get_object(self,pk):
        return ReplyLike.objects.filter(user_id=pk)
    def get(self, request, pk, format=None):
        l = []
        post = self.get_object(pk)
        serializer = ReplyLikeSerializer2(post,many=True)
        for r in serializer.data:
            l.append(r['replyId'])
        return Response(l)

class RemoveSaveVideo(APIView):
    def get_object(self,pk):
        userId = self.request.GET['userId']
        return SavedPost.objects.get(postId=pk,user=userId)

    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class Deletecomment(APIView):
    permission_classes = (IsAuthenticated,)
    def get_object(self,pk):
        userId = self.request.GET['userId']
        return CommentModel.objects.get(id=pk,userId=userId)


    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class Deletereply(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self,pk):
        userId = self.request.GET['userId']
        return ReplyModel.objects.get(id=pk,userId=userId)

    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FcmNotificationApiVIew(APIView):
    #permission_classes = (IsAuthenticated,)
    def get_object(self, pk):
        return FirebaseNotification.objects.get(user=pk)
    
    def get(self, request, pk, format=None):
        
        notification = self.get_object(pk)
        serializer = FirebaseNotificationSerializer(notification)
        
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        notification = self.get_object(pk)
        print(request.data)
        serializer = FirebaseNotificationSerializer(notification,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MusicTrackApiSet(APIView):
    def get(self, request, format=None):
        if "category" in request.GET:
            category = request.GET['category']
            music = MusicTracks.objects.filter(category=category).order_by('-created')
        else:
            music = MusicTracks.objects.all()
        serializers = MusicSerializer(music,many=True)
        return Response(serializers.data)

class PostApiSetSortBySize(APIView):
    def get(self, request, format=None):
        # if "category" in request.GET:
        #     category = request.GET['category']
        #     music = FileUpload.objects.all().order_by('fileSize')[:10]
        # else:
        post = FileUpload.objects.all().order_by('fileSize')[:10]
        serializers = FileUploadSerializer2(post,many=True)
        return Response(serializers.data)
