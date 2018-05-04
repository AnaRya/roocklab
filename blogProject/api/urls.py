from django.conf.urls import include
from django.conf.urls import url
from api import views


urlpatterns = [
    url(r'^boards/$', views.board_list),
    url(r'^boards/(?P<pk>\d+)/$', views.board_detail),
    url(r'^topics/$', views.topic_list),
    url(r'^api-auth/', include('rest_framework.urls')),

]
