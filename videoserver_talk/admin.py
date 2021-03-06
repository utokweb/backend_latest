from django.contrib import admin

# Register your models here.
from .models import PhoneNumber,MusicTracks,FileUpload,PostLike,HashTag,ViewModel,FollowerModel,CommentModel,ReplyModel,CommentLike,ReplyLike,PostUploadTest,FrameId,StickerId,Notification,FirebaseNotification,BlockRequest,PostReportRequest,OriginalAudioPost,PromotionBanner,Wallet,WalletTransaction,InvitationCode,PromotionNotification


admin.site.register(PhoneNumber)
admin.site.register(FileUpload)
admin.site.register(PostLike)
admin.site.register(HashTag)
admin.site.register(ViewModel)
admin.site.register(FollowerModel)
admin.site.register(CommentModel)
admin.site.register(ReplyModel)
admin.site.register(CommentLike)
admin.site.register(ReplyLike)
admin.site.register(PostUploadTest)
admin.site.register(FrameId)
admin.site.register(StickerId)
admin.site.register(Notification)
admin.site.register(FirebaseNotification)
admin.site.register(MusicTracks)
admin.site.register(BlockRequest)
admin.site.register(PostReportRequest)
admin.site.register(OriginalAudioPost)
admin.site.register(PromotionBanner)
admin.site.register(InvitationCode)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
admin.site.register(PromotionNotification)


