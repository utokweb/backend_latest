from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # <-- Here
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from videoserver_talk.serializers import UserSerializer,UserLoginSerializer,ProfileSerializer,FileUploadSerializer,FileUploadSerializer2,UserSearchSerializer,PostLikeSerializer,PostLikeSerializer2,ViewSetSerializer,HashtagSearchSerializer,FollowerSerializer,ProfileSerializer2,CommentSerializer,ReplySerializer,HashtagSearchSerializer2,CommentSerializer2,ReplySerializer2,CommentLikeSerializer,CommentLikeSerializer2,ReplyLikeSerializer,ReplyLikeSerializer2
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import requests
from rest_framework.parsers import FormParser, MultiPartParser
import sys
from rest_framework.pagination import PageNumberPagination
import django_filters
from .models import PhoneNumber,FileUpload,PostLike,HashTag,FollowerModel,CommentModel,ReplyModel,CommentLike,ReplyLike
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
from .pagination import CustomPagination

BASEURL = "http://18.220.150.215:8000"

class HelloView(APIView):
    permission_classes = (IsAuthenticated,)             # <-- And here

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
                # API_ENDPOINT = BASEURL+'/api/method/frappe.core.doctype.user.user.sign_up?email='+request.data['email']+'&full_name='+request.data['username']+'&redirect_to=&password='+request.data['password']+''
                # res = requests.get(API_ENDPOINT,verify=False)
                # print(res.text)
                # response_data = json.loads(res.text)
                token = Token.objects.create(user=user)
                json_res = serializer.data
                json_res['token'] = token.key

                # try:
                #     if 'data' in response_data:

                #         json_res['user'] = response_data
                #     else:
                #         json_res['user'] = {}
                # except:
                #     json_res['user'] = {}
                return Response(json_res, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    except Exception as identifier:
        user = None
        return Response({"user":user})
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
    def get_object(self, pk):
        try:
            
            user = User.objects.get(id=pk)
            profile_id = PhoneNumber.objects.get(user_id=user.id)
            return PhoneNumber.objects.get(pk=profile_id.id)
        except PhoneNumber.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        
        profile = self.get_object(pk)
        serializer = ProfileSerializer(profile)
        user = User.objects.get(id=pk)
        return Response({"user_profile":serializer.data,"user_data":model_to_dict(user)})

    def put(self, request, pk, format=None):
        profile = self.get_object(pk)
        
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
            serialize_data.update({"owner":username.username})
            return Response(serialize_data, status=status.HTTP_201_CREATED)
        print(fileSerializer.errors)
        return Response(fileSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                return FileUpload.objects.filter(Q(privacy="public") | Q(privacy="private"),owner_id=pk).order_by('-created')
            elif status_== 0:
                return FileUpload.objects.filter(privacy="public",owner_id=pk).order_by('-created')
            elif status_ == 2:
                return FileUpload.objects.filter(owner_id=pk).order_by('-created')
        except FileUpload.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        upload = self.get_object(pk)
        results = self.paginate_queryset(upload, request, view=self)
        
        serializer = FileUploadSerializer2(results,many=True)
        for f in serializer.data:
        	profile_pic=PhoneNumber.objects.get(user=pk)
        	profilePic = str(profile_pic.profilePic)
        	f.update({"profilePic":"https://utok-s3-cloud.s3.amazonaws.com/media/"+profilePic,"user_id":pk})

        #pagination_class = StandardResultsSetPagination

        return self.get_paginated_response(serializer.data)

class Timeline(APIView,CustomPagination):

    def get(self, request, format=None):
        fileupload = FileUpload.objects.filter(privacy="public").order_by('-created')
        results = self.paginate_queryset(fileupload, request, view=self)
        serializer = FileUploadSerializer2(results, many=True)
        for f in serializer.data:
        	user_id = User.objects.get(username=f['owner'])
        	profile_pic=PhoneNumber.objects.get(user=user_id)
        	profilePic = str(profile_pic.profilePic)
        	f.update({"profilePic":"https://utok-s3-cloud.s3.amazonaws.com/media/"+profilePic,"user_id":user_id.id})
        return self.get_paginated_response(serializer.data)

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
                        dict_.update({"count":str(hashtag_count.count),"owner":username.username,"user_id":dict_['owner_id'],"code":search,"datafile":"https://utok-s3-cloud.s3.amazonaws.com/media/"+dict_['datafile'],"thumbnail":"https://utok-s3-cloud.s3.amazonaws.com/media/"+dict_['thumbnail']})
                        l.append(dict_)
                        
                           
            except Exception as identifier:
                print(identifier)
                pass
        return Response(l)

class FollowSetApiView(APIView):
    def post(self, request, format=None):
        serializer = FollowerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FollowerGetViewSet(APIView):
    def get_object(self,pk):
        
        return FollowerModel.objects.filter(followingId=pk,follow=1)
        

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = FollowerSerializer(post,many=True)
        for f in serializer.data:
            
            profile_pic=PhoneNumber.objects.get(user=f['followerId'])
            profilePic = str(profile_pic.profilePic)
            print(profilePic)
            if profile_pic:
                    f.update({"profilePic":"https://utok-s3-cloud.s3.amazonaws.com/media/"+profilePic,"userame":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id})
            else:
                f.update({"profilePic":"","userame":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id})
        
        return Response(serializer.data)
        
class FollowingGetViewSet(APIView):
    def get_object(self,pk):
        
        return FollowerModel.objects.filter(followerId_id=pk,follow=1)
        

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = FollowerSerializer(post,many=True)
        #for f in serializer.data:
        for f in serializer.data:
            
            try:
                profile_pic=PhoneNumber.objects.get(user=f['followingId'])
                profilePic = str(profile_pic.profilePic)
                print(profilePic)
                if profilePic:
                    f.update({"profilePic":"https://utok-s3-cloud.s3.amazonaws.com/media/"+profilePic,"userame":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id})
                else:
                    f.update({"profilePic":"","userame":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id})
            except PhoneNumber.DoesNotExist:
                pass

        return Response(serializer.data)

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

class TopTrendingPostApiSet(APIView):
     
    def get(self, request, format=None):
        post = FileUpload.objects.all().order_by('-viewCount')[:5]
        
        serializer = FileUploadSerializer2(post,many=True)
        for f in serializer.data:
                user_id = User.objects.get(username=f['owner'])
                profile_pic=PhoneNumber.objects.get(user=user_id)
                profilePic = str(profile_pic.profilePic)
                f.update({"profilePic":"https://utok-s3-cloud.s3.amazonaws.com/media/"+profilePic,"user_id":user_id.id})
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
                f.update({"profilePic":"https://utok-s3-cloud.s3.amazonaws.com/media/"+profilePic,"user_id":user_id.id})
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
        return  FileUpload.objects.filter(owner=pk).order_by('-viewCount')
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