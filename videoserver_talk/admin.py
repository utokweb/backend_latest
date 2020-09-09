from django.contrib import admin

# Register your models here.
from .models import PhoneNumber,FileUpload,PostLike,HashTag,ViewModel,FollowerModel,CommentModel,ReplyModel,CommentLike,ReplyLike

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


