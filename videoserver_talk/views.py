from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # <-- Here
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from videoserver_talk.serializers import UserSerializer,UserLoginSerializer,MusicSerializer,ProfileSerializer,FileUploadSerializer,FileUploadSerializer2,UserSearchSerializer,PostLikeSerializer,PostLikeSerializer2,ViewSetSerializer,HashtagSearchSerializer,FollowerSerializer,ProfileSerializer2,CommentSerializer,ReplySerializer,HashtagSearchSerializer2,CommentSerializer2,ReplySerializer2,CommentLikeSerializer,CommentLikeSerializer2,ReplyLikeSerializer,ReplyLikeSerializer2,PostsaveSerializer2,PostsaveSerializer,TestPostSerializer,NotificationSerializer,FirebaseNotificationSerializer,BlockRequestSerializer,PostReportSerializer,OriginalAudioPostSerializer,PromotionBannerSerializer,WalletSerializer,WalletTransactionSerializer,InvitationCodeSerializer,UsernameSearchSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import requests
from rest_framework.parsers import FormParser, MultiPartParser
import sys
from rest_framework.pagination import PageNumberPagination
import django_filters
from .models import PhoneNumber,FileUpload,MusicTracks,PostLike,HashTag,FollowerModel,CommentModel,ReplyModel,CommentLike,ReplyLike,SavedPost,PostUploadTest,FrameId,StickerId,Notification,FirebaseNotification,BlockRequest,PostReportRequest,OriginalAudioPost,PromotionBanner,Wallet,WalletTransaction,InvitationCode
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
from . import utils
from youtalk.creds import PAYTM_ID,PAYTM_KEY,PAYTM_URL,PAYOUT_STATUS_URL,PAYTM_SUBWALLET_GUID
from . import constants
from paytmchecksum import PaytmChecksum
from firebase_admin import messaging
from youtalk import settings


VERSION = 38 #Refers to Application Version Code
VERSION_STRING = "1.3.8"
STRICT = True #If True, Application won't proceed without user Updating the Application to Latest Build
INVITATION_REWARD = 5
MIN_WALLET_THRESHOLD = 50
PAYTM_BLOCKLIST = ["7626968921"]


@api_view(['GET'])
def checkApplicationVersion(request):
    return Response({
        "version_code":VERSION,
        "version_string":VERSION_STRING,
        "strict":STRICT
    })
        
@api_view(['GET'])
def getVersionPromoBanner(request):
    try:
        version = request.GET.get("v")
        promoBanners = PromotionBanner.objects.filter(appVersion=version)[1:]
        serializer = PromotionBannerSerializer(promoBanners, many=True)
        return Response(serializer.data)
    except:
        return Response([])   

@api_view(['GET'])
def getCategoryPromoBanners(request):
    try:
        category = request.GET.get("category")
        promoBanners = PromotionBanner.objects.filter(category=category)
        serializer = PromotionBannerSerializer(promoBanners, many=True)
        return Response(serializer.data)
    except:
        return Response([])            

class UserCreate(APIView):
    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        invitation_code = None
        try:
            invitation_code = request.data['invitation_code']
        except:
            pass    
        has_invitation_code = invitation_code is not None
        session_confirmation = True
        if VERSION == 30: # Only for Version 30 as a backup for previous APIs
            sessionID = request.data['session_id']
            otpCode = request.data['otp_code']
            sessionConResponse = requests.get("http://2factor.in/API/V1/4a653039-2e36-11eb-83d4-0200cd936042/ADDON_SERVICES/RPT/TSMS/"+sessionID+"")            
            session_confirmation = "<logStatus>Valid</logStatus>" in sessionConResponse.text and otpCode in sessionConResponse.text
        if serializer.is_valid() and session_confirmation:
            user = serializer.save()
            if user:
                PhoneNumber.objects.create(user=user,phone_number=request.data['phone_number'],fullName=request.data['full_name'])
                token = Token.objects.create(user=user)
                json_res = serializer.data
                json_res['token'] = token.key
                user = User.objects.get(id=json_res['id'])
                
                #Creating Wallet with Transactions for Signup
                try:
                    initial_balance = 0
                    if has_invitation_code:
                        initial_balance = INVITATION_REWARD
                    #Creating Wallet for New User with Initital Balance    
                    newWalletSerialized = WalletSerializer(data={'user':user.id,'balance':initial_balance})
                    if newWalletSerialized.is_valid():
                        newWalletSerialized.save()
                        newWallet = Wallet.objects.get(user=user.id)
                        #Creating Transaction on Wallet for New User
                        transaction_id = "ORDERID_" + utils.random_alphanumeric(14,False)
                        transactionData = {'transID':transaction_id,'wallet':newWallet.id,'transType':constants.TRANS_TYPE_CREDIT,'transDesc':"SignUp Credit",'amount':INVITATION_REWARD,'transTo':constants.TRANS_TO_WALLET,'transStatus':constants.TRANS_STATUS_SUCCESS}
                        newWalletTrans = WalletTransactionSerializer(data=transactionData)
                        if newWalletTrans.is_valid():
                            newWalletTrans.save()
                    if has_invitation_code:
                        try:
                            #Updating Invitation Code Data for the User who
                            #Invited
                            invitationCodeData = InvitationCode.objects.get(code=invitation_code)
                            invitationCodeData.timesUsed += 1
                            invitationCodeData.save()
                            #Updating Wallet of User who Invited
                            invOwnerWallet = Wallet.objects.get(user=invitationCodeData.user)
                            invOwnerWallet.balance += INVITATION_REWARD
                            invOwnerWallet.save()
                            #Adding Transaction on Wallet of User who Invited
                            transaction_id = "ORDERID_" + utils.random_alphanumeric(14,False)
                            transactionData.update({'transID':transaction_id,'wallet':invOwnerWallet.id,'transDesc':"SignUp Credit for "+user.username})
                            ownerTransSerializer = WalletTransactionSerializer(data=transactionData)
                            if ownerTransSerializer.is_valid():
                                ownerTransSerializer.save()
                            #Sending Notification to Owner  
                            token=FirebaseNotification.objects.get(user=invitationCodeData.user)
                            registration_token = token.token
                            title = "Congratulations!"
                            body = "You have earned Referral Reward! Check your FilmMee Wallet Now!"
                            message = messaging.Message(
                                notification=messaging.Notification(
                                    title=title,
                                    body=body,
                                ),
                                data={
                                    'title':title,
                                    'message': body,
                                    'types':"Wallet",
                                },
                                token=registration_token,   
                            )
                            response = messaging.send(message)    
                        except (InvitationCode.DoesNotExist,Wallet.DoesNotExist):
                            pass    
                except:
                    pass    

                #Creating Firebase Notification with User Signup
                try:
                    FirebaseNotification.objects.get(user=user)
                except:
                    FirebaseNotification.objects.create(user=user)

                return Response(json_res, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BlockRequests(APIView):
    
    def get(self, request,pk, format=None):
        blockedUsers = BlockRequest.objects.filter(blockedBy=pk)
        serializer = BlockRequestSerializer(blockedUsers, many=True)
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
    permission_classes = (permissions.AllowAny, )
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            userResp = serializer.data
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    def get(self,request,pk):
        try:
            fileUpload = FileUpload.objects.get(id=pk)
            fileSerializer = FileUploadSerializer2(fileUpload)
            fileData = fileSerializer.data
            user_id = User.objects.get(username=fileData['owner'])
            profile_pic=PhoneNumber.objects.get(user=user_id)
            profilePic = str(profile_pic.profilePic)
            if profilePic=="":
        	    fileData.update({"profilePic":None,"user_id":user_id.id})
            else:
                fileData.update({"profilePic":STORAGE_URL+"profile_dp/"+profilePic,"user_id":user_id.id})
            return Response({'status':0,'data':fileData})
        except FileUpload.DoesNotExist as e:
            print(e)
        return Response({'status':1})
            
    def post(self, request, *args, **kwargs):
        fileSerializer = FileUploadSerializer(data=request.data)
        tagged_users = []
        try:
            tagged_string = request.data['tagged']
            if tagged_string is not None and tagged_string is not "":
                tagged_users = tagged_string.split(sep=",")
        except:
            pass    

        if fileSerializer.is_valid():
            fileSerializer.save()
            res = dict(fileSerializer.data)
            username = User.objects.get(id=res['owner'])
            serialize_data = fileSerializer.data
            
                
            try:
                # Checking if this post has a Promotional Hashtag
                # and if yes we will be updating the Promotional Banner Post Count
                promoBannerID = request.data['promoBannerID']
                if promoBannerID != "-1":
                    promoBannerData = PromotionBanner.objects.get(id=promoBannerID)
                    promoBannerData.postsCount += 1
                    promoBannerData.save()
            except:
                pass

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

            for tag in tagged_users:
                try:
                    notificationType = "UserTag"    
                    notificationMessage = username.username + " tagged you in a new Post!"
                    user_data = User.objects.get(username=tag)
                    newPost = FileUpload.objects.get(id=serialize_data['id'])
                    Notification.objects.create(toId=user_data,postId=newPost,types=notificationType,message=notificationMessage)
                    token=FirebaseNotification.objects.get(user=user_data.id)
                    registration_token = token.token
                    thumbnail = str(serialize_data['thumbnail'])
                    hasThumbnail = thumbnail is not None and thumbnail is not ""
                    short_link = utils.get_short_link("/post_update/"+username.username+"/"+str(serialize_data['id'])+"")
                    title = "You've been Tagged!"
                    message = messaging.Message(
                        notification=messaging.Notification(
                            title=title,
                            body=notificationMessage,
                        ),
                        data={
                            'title':title,
                            'message': notificationMessage,
                            'types':notificationType,
                            'shortLink':short_link,
                            'thumbnail':STORAGE_URL+"upload_thumbnail/"+thumbnail if hasThumbnail else "",
                        },
                        token=registration_token,   
                    )
                    response = messaging.send(message)
                    
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

@api_view(['GET'])
def checkInvitationCode(request):
    try:
        code = request.GET.get('code')
        if code is not None:
            InvitationCode.objects.get(code=code)
            return Response({'status':0})
        else:
            return Response({'status':1})        
    except InvitationCode.DoesNotExist:
        return Response({'status':1})


class InviationCodeViewSet(APIView):
    def get(self,request,pk):
        try:
            invitationObject = InvitationCode.objects.get(user=pk)
            serializedData = InvitationCodeSerializer(invitationObject)
            return Response({'status':0,'data':serializedData.data})
        except InvitationCode.DoesNotExist:
            new_code = utils.random_alphanumeric(9)
            invitationCodeSerialized = InvitationCodeSerializer(data={'user':pk,'code':new_code})
            if invitationCodeSerialized.is_valid():
                invitationCodeSerialized.save()
                return Response({'status':0,'data':invitationCodeSerialized.data})
            return Response({'status':1,'message':"Code Does not Exist",'errors':invitationCodeSerialized.errors})

    def post(self,request,*args,**kwargs):
        invitationCodeSerialized = InvitationCodeSerializer(data=request.data)
        if invitationCodeSerialized.is_valid():
            invitationCodeSerialized.save()
            return Response(invitationCodeSerialized.data, status=status.HTTP_201_CREATED)
        return Response(invitationCodeSerialized.errors, status=status.HTTP_400_BAD_REQUEST) 
        
    def put(self, request, pk, format=None):
        invitationObject = InvitationCode.objects.get(id=pk)
        invitationCodeSerialized = WalletSerializer(invitationObject, data=request.data)
        if invitationCodeSerialized.is_valid():
            invitationCodeSerialized.save()
            return Response(invitationCodeSerialized.data,status=status.HTTP_200_OK)
        return Response(invitationCodeSerialized.errors, status=status.HTTP_400_BAD_REQUEST)              
        
class WalletViewSet(APIView):

    def get(self,request,pk):
        try:
            walletObj = Wallet.objects.get(user=pk)
            serializedData = WalletSerializer(walletObj)
            return Response({'status':0,'data':serializedData.data})
        except Wallet.DoesNotExist:
            walletSerializedData = WalletSerializer(data={'user':pk,'balance':0})
            if walletSerializedData.is_valid():
                walletSerializedData.save()
                return Response({'status':0,'data':walletSerializedData.data})
            return Response({'status':1,'message':"Wallet Does not Exist",'errors':walletSerializedData.errors})

    def post(self,request,*args,**kwargs):
        walletSerializedData = WalletSerializer(data=request.data)
        if walletSerializedData.is_valid():
            walletSerializedData.save()
            return Response(walletSerializedData.data, status=status.HTTP_201_CREATED)
        return Response(walletSerializedData.errors, status=status.HTTP_400_BAD_REQUEST) 
        
    def put(self, request, pk, format=None):
        walletObj = Wallet.objects.get(id=pk)
        phone_number = request.data['paytm_number']
        if phone_number is not None:
            try:
                phoneNumberWallet = Wallet.objects.get(paytm=phone_number)
                return Response({'status':2},status=status.HTTP_400_BAD_REQUEST)
            except Wallet.DoesNotExist:
                walletObj.paytm = phone_number
                walletObj.save()
                return Response({'status':0},status=status.HTTP_200_OK)
        return Response({"status":1}, status=status.HTTP_400_BAD_REQUEST)                                 


class WalletTransactionView(APIView):

    def get(self,request,pk):
        try:
            walletTransactions = WalletTransaction.objects.filter(wallet=pk).order_by("-created")
            serializerData = WalletTransactionSerializer(walletTransactions,many=True)
            return Response(serializerData.data)
        except Exception as e:
            print(e)
            return Response([])

    def post(self,request,*args,**kwargs):
        transactionSerialized = WalletTransactionSerializer(data=request.data)
        if(transactionSerialized.is_valid()):
            wallet = Wallet.objects.get(id=request.data['wallet'])
            if request.data['transType'] == "CREDIT":
                wallet.balance += request.data['amount']
            elif request.data['transType'] == "DEBIT":
                if wallet.balance >= request.data['amount']:
                    wallet.balance -= request.data['amount']
                else: 
                    return Response({"status":1,"data":["Not Enough Balance to Debit"]}, status=status.HTTP_400_BAD_REQUEST) 
            transactionSerialized.save()
            wallet.save()
            return Response({"status":0,"data":transactionSerialized.data}, status=status.HTTP_201_CREATED)
        return Response({"status":1,"data":transactionSerialized.errors}, status=status.HTTP_400_BAD_REQUEST) 

@api_view(['POST'])
def payout_to_paytm(request):
    try:
        wallet = request.data['wallet']
        walletDetails = Wallet.objects.get(id=wallet)
        number = walletDetails.paytm
        if number in PAYTM_BLOCKLIST:
            raise Exception("Your number has been restricted from Transaction")
        amount = walletDetails.balance
        if amount >= MIN_WALLET_THRESHOLD:
            orderID = "ORDERID_"+utils.random_alphanumeric(14,False)
            paytmParams = dict()
            paytmParams["subwalletGuid"]      = PAYTM_SUBWALLET_GUID
            paytmParams["orderId"]            = orderID
            paytmParams["beneficiaryPhoneNo"] = "5555566666" if settings.DEBUG is True else number
            paytmParams["amount"]             = "1.00" if settings.DEBUG is True else str(amount)
            post_data = json.dumps(paytmParams)
            checksum = PaytmChecksum.generateSignature(post_data, PAYTM_KEY)
            x_mid      = PAYTM_ID
            x_checksum = checksum
            url = PAYTM_URL
            response = requests.post(url, data = post_data, headers = {"Content-type": "application/json", "x-mid": x_mid, "x-checksum": x_checksum}).json()
            if response['status'] != "FAILURE":
                transactionData = {'transID':orderID,'wallet':wallet,'transType':constants.TRANS_TYPE_DEBIT,'transDesc':"Transfer to PayTM Balance",'amount':amount,'transTo':constants.TRANS_TO_PAYTM,'transStatus':constants.TRANS_STATUS_ACCEPTED}        
                try:
                    walletDetails.balance = 0
                    walletDetails.save()
                    walletTransSerializer = WalletTransactionSerializer(data=transactionData)
                    if walletTransSerializer.is_valid():
                        walletTransSerializer.save()
                except:
                    pass        
                return Response({'status':0,'data':response})
            else:
                return Response({'status':1,'error':"Problem Initiating Transfer"})     
        else:
            return Response({'status':1,'error':"You must have a minimum balance of "+str(MIN_WALLET_THRESHOLD)+" INR to Checkout"})     
    except Exception as e:
        print(e)
        return Response({'status':1,'error':"Problem Initiating Transfer"})

@api_view(['GET'])
def check_payout_status(request):
    try:
        orderID = request.GET.get('orderId')
        paytmParams = dict()
        paytmParams["orderId"] = orderID
        post_data = json.dumps(paytmParams)
        checksum = PaytmChecksum.generateSignature(post_data, PAYTM_KEY)
        x_mid      = PAYTM_ID
        x_checksum = checksum
        url = PAYOUT_STATUS_URL
        response = requests.post(url, data = post_data, headers = {"Content-type": "application/json", "x-mid": x_mid, "x-checksum": x_checksum}).json()
       # print(response)
        if response['status'] in [constants.TRANS_STATUS_SUCCESS,constants.TRANS_STATUS_PENDING,constants.TRANS_STATUS_FAIL,constants.TRANS_STATUS_CANCELLED]:
            walletTransData = WalletTransaction.objects.get(transID=orderID)
            walletTransData.transStatus = response['status']
            walletTransData.save()
            if response['status'] in [constants.TRANS_STATUS_FAIL,constants.TRANS_STATUS_CANCELLED]:
                walletData = Wallet.objects.get(id=walletTransData.wallet.id)
                walletData.balance = walletTransData.amount
                walletData.save()
        return Response({'status':0,'data':response})
    except Exception as e:
        print(e)
        return Response({'status':1})


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
        return Notification.objects.filter(toId=pk).order_by('-created')[:50]
    
    def get(self, request, pk, format=None):
        notification = self.get_object(pk)
        results = self.paginate_queryset(notification, request, view=self)
        serializer = NotificationSerializer(results,many=True)
        for f in serializer.data:
            if f['fromId'] is not None:
                profile_pic=PhoneNumber.objects.get(user_id=f['fromId'])
                profilePic = str(profile_pic.profilePic)
                if profilePic=="":
                    f.update({"profilePic":None,"username":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id,"elevation":profile_pic.elevation})
                    f.update({"thumbnail":None})
                else:
                    f.update({"thumbnail":STORAGE_URL+"profile_dp/"+profilePic,"username":profile_pic.user.username,"fullName":profile_pic.fullName,"userId":profile_pic.user.id,"elevation":profile_pic.elevation})        
                    f.update({"thumbnail":STORAGE_URL+"profile_dp/"+profilePic})
            if f['postId'] is not None:        
                postData=FileUpload.objects.get(id=f['postId'])
                thumbnail = str(postData.thumbnail)
                if thumbnail == "":
                    f.update({"thumbnail":None})
                else:
                    f.update({"thumbnail":STORAGE_URL+"upload_thumbnail/"+thumbnail})


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
        orderBy = []
        orders = ["likeCount","-likeCount","viewCount","-viewCount","created","-created","shareCount","-shareCount","description","-description","category","-category"]
        random.shuffle(orders)
        factor = random.randint(1,4)
        for i in range(factor):
            random_choice = random.choice(orders)
            rc_backup = random_choice
            if "-" in random_choice:
                random_choice = random_choice.replace("-","")
            if random_choice not in orderBy and ("-"+random_choice) not in orderBy:
                orderBy.append(rc_backup)
        orderby = set(orderBy)     
        orderby = list(orderBy)
        print("TIMELINE RESULTS ORDERED BY")
        print(orderBy)
        # orderBy = ["-created"]
        # # In future we need to get the timezone from client side to query the
        # # posts accordingly
        min_date = utils.getDateAtGap(-70 if settings.DEBUG is True else -14)
        # orderBy = ["viewCount"]
        # now = datetime.datetime.now(tz=pytz.timezone("Asia/Kolkata"))
        # if now.minute <20:
        #     if 21 <= now.hour <= 3:
        #         orderBy = ["profId__gender"]
        #     else:
        #         orderBy = ["-viewCount","-created"]
        # elif 20<= now.minute <=40:
        #     if 12 <= now.hour <= 15:
        #         orderBy = ["created"]
        #     else:
        #         orderBy = ["-created"]

        fileupload = FileUpload.objects.filter(privacy="public",reportsCount__lt=5,created__gt=min_date).order_by(*orderBy)
        if pk != None and pk > 0 :
            blockRequests = BlockRequest.objects.filter(blockedBy=pk)
            userIds = blockRequests.values_list('blockedUser',flat=True)
            # TO EXCLUDE REPORTED POSTS - NOT WORKING DUE TO MULTIPLE "IN" EXCLUDES
            # reportedPosts = PostReportRequest.objects.filter(reportedBy=pk)
            # reportedPostIds = reportedPosts.values_list('post',flat=True)
            fileupload = FileUpload.objects.filter(privacy="public",reportsCount__lt=5,created__gt=min_date).order_by(*orderBy).exclude(owner_id__in=userIds)
        results = self.paginate_queryset(fileupload, request, view=self)
        serializer = FileUploadSerializer2(results, many=True)
        for f in serializer.data:    
            try:
                user_id = User.objects.get(username=f['owner'])
                profile_pic=PhoneNumber.objects.get(user=user_id)
                profilePic = str(profile_pic.profilePic)
                if profilePic=="":
                    f.update({"profilePic":None,"user_id":user_id.id})
                else:
                    f.update({"profilePic":STORAGE_URL+"profile_dp/"+profilePic,"user_id":user_id.id})
            except:
                pass        
        final_data = serializer.data
        random.shuffle(final_data)      
        return self.get_paginated_response(final_data)

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
            except:
                status_= 0
            
            if status_==0:
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
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PostLikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def increment_post_shares(request):
    try:
        post_id = request.data['postID']
        fileData = FileUpload.objects.get(id=post_id)
        fileData.shareCount += 1
        fileData.save()
        if fileData.shareCount in [3,10,16,40,52,61,72,85,95,100]:
            notificationType = "PostShare"    
            notificationMessage = "Your post has been shared more than "+ str(fileData.shareCount) + " times!"
            try:
                Notification.objects.filter(postId=fileData.id,types=notificationType).delete()
            except Notification.DoesNotExist:
                pass    
            Notification.objects.create(toId=fileData.owner,postId=fileData,types=notificationType,message=notificationMessage)
            token=FirebaseNotification.objects.get(user=fileData.owner)
            registration_token = token.token
            thumbnail = str(fileData.thumbnail)
            hasThumbnail = thumbnail is not None and thumbnail is not ""
            short_link = utils.get_short_link("/post_update/"+fileData.owner.username+"/"+str(fileData.id))
            title = 'Congratulations!'
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=notificationMessage,
                ),
                data={
                    'title':title,
                    'message': notificationMessage,
                    'types':notificationType,
                    'shortLink':short_link,
                    'thumbnail':STORAGE_URL+"upload_thumbnail/"+thumbnail if hasThumbnail else "",
                },
                token=registration_token,   
            )
            response = messaging.send(message)
        return Response({"status":0}) 
    except Exception as e:  
        print(e)
        pass
    return Response({"status":1})   



class UserSearch(generics.ListCreateAPIView):
    queryset = PhoneNumber.objects.all()
    serializer_class = UserSearchSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['fullName','user__username']

@api_view(["GET"])
def username_search(request):
    try:
        q = request.GET['q']
        users = User.objects.filter(username__contains=q)[:5]
        users_serializer = UsernameSearchSerializer(users,many=True)
        l=[]
        for user in users_serializer.data:
            userData = {"username":user['username']}
            phoneNumber = PhoneNumber.objects.get(user=user['id'])
            if phoneNumber.profilePic is not None and phoneNumber.profilePic is not "":
                profilePic = str(phoneNumber.profilePic)
                userData.update({"profilePic":STORAGE_URL+"profile_dp/"+profilePic})
            l.append(userData)                    
        return Response(l)
    except Exception as e:
        print(e)
        return Response([])    


class UserPostLike(APIView):

    def get_object(self, pk):
        try:
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

class HashTagPostSearch(APIView,CustomPagination2):
    # def get(self, request, format=None):
    #     l = []
    #     fileupload = FileUpload.objects.filter(privacy="public").values()
    #     search = request.GET['search']
    #     for f in fileupload:
    #         list_ = f['hashtag']
    #         list_1 = list_.split(",")
    #         try:
    #             for z in list_1:
    #                 if search == z:
    #                     dict_ = f
    #                     hashtag_count = HashTag.objects.get(hashtag=search)
    #                     username = User.objects.get(id=dict_['owner_id'])
    #                     elevation = PhoneNumber.objects.get(user=dict_['owner_id'])
    #                     profId = {"followerCount":elevation.followerCount,"followingCount":elevation.followingCount,"elevation":elevation.elevation}
    #                     dict_.update({"count":str(hashtag_count.count),"owner":username.username,"user_id":dict_['owner_id'],"code":search,"datafile":STORAGE_URL+"upload_vedio/"+dict_['datafile'],"thumbnail":STORAGE_URL+"upload_thumbnail/"+dict_['thumbnail'],"latitude":str(dict_['latitude']),"longitude":str(dict_['longitude']),'profId':profId})
    #                     l.append(dict_)         
    #         except Exception as identifier:
    #             pass
    #     return Response(l)

    def get(self, request, format=None):
        search = request.GET['search']
        uploads = FileUpload.objects.filter(privacy="public",hashtag__contains=search).order_by("-created")[:100]
        posts = uploads.values()
        hashtag_count = HashTag.objects.get(hashtag=search)
        l = []
        for f in posts:
            try:
                username = User.objects.get(id=f['owner_id'])
                elevation = PhoneNumber.objects.get(user=f['owner_id'])
                profId = {"followerCount":elevation.followerCount,"followingCount":elevation.followingCount,"elevation":elevation.elevation}
                f.update({"count":str(hashtag_count.count),"owner":username.username,"user_id":f['owner_id'],"code":search,"datafile":STORAGE_URL+"upload_vedio/"+f['datafile'],"thumbnail":STORAGE_URL+"upload_thumbnail/"+f['thumbnail'],"latitude":str(f['latitude']),"longitude":str(f['longitude']),'profId':profId})
                l.append(f)         
            except:
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
        post = PhoneNumber.objects.all().order_by('-followerCount')[:20]
        serializer = ProfileSerializer2(post,many=True)
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
        post = FileUpload.objects.all().order_by('-viewCount')[:10]
        
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
        hashTag = HashTag.objects.all().order_by('-count')[:5]
        
        serializer = HashtagSearchSerializer2(hashTag,many=True)
        for hashtags in serializer.data:
            search = FileUpload.objects.filter(hashtag__contains=hashtags['hashtag']).order_by('-viewCount')[:10]
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
        return Response(serializer.data)

class CheckFollowingStatus(APIView):
    def get(self, request, format=None):
        userId = self.request.GET['userId']
        followingId = self.request.GET['followingId']
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
        serializer = FirebaseNotificationSerializer(notification,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
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

@api_view(['GET'])        
def music_search(request):
    search = request.GET['search']
    musicTracks = MusicTracks.objects.filter(musicName__icontains=search).order_by("-created") | MusicTracks.objects.filter(metaData__icontains=search).order_by("-created") 
    musicSearchSerializer = MusicSerializer(musicTracks,many=True)
    return Response(musicSearchSerializer.data) 

class PostApiSetSortBySize(APIView):
    def get(self, request, format=None):
        # if "category" in request.GET:
        #     category = request.GET['category']
        #     music = FileUpload.objects.all().order_by('fileSize')[:10]
        # else:
        post = FileUpload.objects.all().order_by('fileSize')[:10]
        serializers = FileUploadSerializer2(post,many=True)
        return Response(serializers.data)
