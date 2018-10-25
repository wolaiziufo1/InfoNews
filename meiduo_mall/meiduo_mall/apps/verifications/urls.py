from django.conf.urls import url
from verifications.views import SMSCodeView

urlpatterns = [
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$',SMSCodeView.as_view())
]