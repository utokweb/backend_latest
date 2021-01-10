from django.shortcuts import render
from rest_framework.views import APIView
from . import pagination
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.forms.models import model_to_dict
from videoserver_talk import models
from videoserver_talk import serializers
from youtalk.storage_backends import STORAGE_URL

#View to Log In a Master Panel User
@api_view(['POST'])
def login(request):
    try:
        username=request.data['usr']
        password=request.data['pwd']
        user = authenticate(username=username, password=password)
        if user is not None:
            token,created = Token.objects.get_or_create(user=user)
            user_dict = model_to_dict(user)
            user_dict['token'] = token.key
            return Response({"status":0,"user":user_dict})
    except Exception as e:
        print(e)
    return Response({"status":1})

class Users(APIView,pagination.CustomPagination):
    def get(self,request):
        try:
            users = models.PhoneNumber.objects.all().order_by('-fullName')
            results = self.paginate_queryset(users, request, view=self)
            serializer = serializers.ProfileSerializer2(results, many=True)
            for f in serializer.data:    
                if f['profilePic'] is not None:
                    f.update({"profilePic":f['profilePic']})
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            print(e)    
        return Response({"results":[],"count":0})

@api_view(['GET'])
def search_user(request):
    try:
        username = request.GET['username']
        users = models.PhoneNumber.objects.filter(user__username__contains=username)
        serializer = serializers.ProfileSerializer2(users, many=True)
        for f in serializer.data:    
            if f['profilePic'] is not None:
                f.update({"profilePic":f['profilePic']})
        return Response({"results":serializer.data,"count":len(serializer.data)})    
    except Exception as e:
        print(e)    
    return Response({"results":[],"count":0})    
           

class PostsForUser(APIView,pagination.CustomPagination):
    def get(self,request,userId):
        try:
            posts = models.FileUpload.objects.filter(owner__id=userId).order_by('-created')
            results = self.paginate_queryset(posts, request, view=self)
            serializer = serializers.FileUploadSerializer2(results, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            print(e)    
        return Response([])
        
@api_view(['PUT'])
def update_post(request,postId):
    try:
        postItem = models.FileUpload.objects.get(id=postId)
        postItem.viewCount = request.data['viewCount']
        postItem.likeCount = request.data['likeCount']
        postItem.save()
        return Response({"status":0,"message":"Post Updated"})
            
    except Exception as e:
        print(e)                
    return Response({"status":1,"message":"Problem Updating Post"})



