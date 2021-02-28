from django.urls import path,re_path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('api/login', views.login, name='login'),
    path('api/users', views.Users.as_view(), name='all-users-paginated'),
    path('api/getUsersExcel', views.get_users_excel, name='all-users'),
    path('api/usersSearch', views.search_user, name='users-search'),
    path('api/userPosts/<int:userId>/', views.PostsForUser.as_view(), name='all-user-posts-paginated'),
    path('api/updateUserPost/<int:postId>/', views.update_post, name='post-update'),
    path('api/filteredPosts', views.PostsForFilters.as_view(), name='filtered-posts-paginated'),
    path('api/promotionNotifications', views.PromotionNotificationView.as_view(), name='promotion-notifications'),
    path('api/promoteMessage', views.promote_message, name='promote-post'),
    path('api/promotePost', views.promote_post, name='promote-message'),
]