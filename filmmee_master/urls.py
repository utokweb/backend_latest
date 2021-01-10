from django.urls import path,re_path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('api/login', views.login, name='login'),
    path('api/users', views.Users.as_view(), name='all-users-paginated'),
    path('api/usersSearch', views.search_user, name='users-search'),
    path('api/userPosts/<int:userId>/', views.PostsForUser.as_view(), name='all-user-posts-paginated'),
    path('api/updateUserPost/<int:postId>/', views.update_post, name='post-update')
    # path('api/master/users', views.UserCreate.as_view(), name='account-create'),
    # path('api/userProfile/<int:pk>/', views.UserProfile.as_view(), name='user-profile'),
    # path('api/userProfile/<str:pk>/', views.UserProfile.as_view(), name='user-profile-username'),
]