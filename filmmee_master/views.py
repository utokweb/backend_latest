from django.shortcuts import render
from rest_framework.views import APIView
from . import pagination
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse,HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.forms.models import model_to_dict
from videoserver_talk import models
from videoserver_talk import serializers
from youtalk.storage_backends import STORAGE_URL
from xlwt import Workbook 
import datetime
from firebase_admin import messaging
from videoserver_talk import utils
from videoserver_talk import constants

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

@api_view(['GET'])    
def get_users_excel(request):
    try:
        users = models.PhoneNumber.objects.all().order_by('-fullName')
        serializer = serializers.PhoneNumberExcelSerializer(users, many=True)
        wb = Workbook() 
        users_worksheet = wb.add_sheet('Users') 

        #Setting Headers
        users_worksheet.write(0,0,"Full Name") 
        users_worksheet.write(0,1,"Phone Number") 
        users_worksheet.write(0,2,"Username") 
        users_worksheet.write(0,3,"Email") 

        #Adding Rows    
        for index,f in enumerate(serializer.data):
            row_count = index + 1
            users_worksheet.write(row_count,0,f['fullName']) 
            users_worksheet.write(row_count,1,f['phone_number']) 
            users_worksheet.write(row_count,2,f['user']['username']) 
            users_worksheet.write(row_count,3,f['user']['email']) 

        #Creating New File Start
        microseconds = datetime.datetime.now().microsecond   
        file_name = "users_"+str(microseconds)+".xls"
        excel_url = "xls/"+file_name
        excel_file = open(excel_url, "x")
        wb.save(excel_url)
        excel_file.close()
        #Creating new File End
        #File For Read as Binary Start
        excel_file = open(excel_url,'rb')
        excel_file_data = excel_file.read()
        response = HttpResponse(excel_file_data,content_type='application/vnd.ms-excel')
        excel_file.close()
        #File For Read as Binary End
        return response
    except Exception as e:
        print(e)
        pass
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

class PromotionNotificationView(APIView,pagination.CustomPagination):
    def get(self,request):
        try:
            notifications = models.PromotionNotification.objects.all().order_by('-created')
            results = self.paginate_queryset(notifications, request, view=self)
            serializer = serializers.PromotionNotificationSerializer(results, many=True)
            for notification in serializer.data:
                if notification['postID'] is not None:
                    postData = models.FileUpload.objects.get(id=notification['postID'])
                    notification['postURL'] = STORAGE_URL+"upload_vedio/"+str(postData.datafile)
                
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

class PostsForFilters(APIView,pagination.CustomPagination):
    def get(self,request):
        posts = []
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        hashtag_filter = request.GET.get('hashtag')
        try:
            posts = models.FileUpload.objects.filter(privacy="public",hashtag__contains=hashtag_filter,created__range=(start_date,end_date)).order_by("-created")    
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

@api_view(['POST'])
def promote_post(request):
    try:
        post_id = request.data["postID"]
        title = request.data["title"]
        body = request.data["body"]
        fileData = models.FileUpload.objects.get(id=post_id)
        thumbnail = str(fileData.thumbnail)
        hasThumbnail = thumbnail is not None and thumbnail is not ""
        short_link = utils.get_short_link("/post_promotion/"+fileData.owner.username+"/"+str(post_id))
        pnSerializer = serializers.PromotionNotificationSerializer(data={'title':title,'message':body,'topic':constants.SUBS_PROMOTION,'postID':post_id})
        if pnSerializer.is_valid():
            pnSerializer.save()
            message = messaging.Message(
                data={
                    'message': body,
                    'title':title,
                    'types':"Promo",
                    'shortLink':short_link,
                    'thumbnail':STORAGE_URL+"upload_thumbnail/"+thumbnail if hasThumbnail else "",
                },
                condition="'"+constants.SUBS_PROMOTION+"' in topics"   
            )
            response = messaging.send(message)
            return Response({'status':0})
    except:
        pass       
    return Response({'status':1})

@api_view(['POST'])
def promote_message(request):
    try:
        title = request.data["title"]
        body = request.data["body"]
        pnSerializer = serializers.PromotionNotificationSerializer(data={'title':title,'message':body,'topic':constants.SUBS_PROMOTION})
        if pnSerializer.is_valid():
            pnSerializer.save()
            message = messaging.Message(
            data={
                'message': body,
                'title':title,
                'types':"Promo",
            },
            condition="'"+constants.SUBS_PROMOTION+"' in topics"   
            )
            response = messaging.send(message)
            return Response({'status':0})
    except:
        pass
    return Response({'status':1})         
    



