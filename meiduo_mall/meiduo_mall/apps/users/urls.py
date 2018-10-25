from django.conf.urls import url
from users import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^username/(?P<username>\w{5,20})/count/$', views.UserNameCountView.as_view()),
    url(r'^mobile/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^users/$', views.UserView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
]
