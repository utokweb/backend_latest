from django.conf.urls import  url

from adzone.views import ad_view

urlpatterns = [
    url(r'^view/(?P<id>[\d]+)/$', ad_view, name='adzone_ad_view'),
]
