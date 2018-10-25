from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from random import randint
from rest_framework.response import Response
# Create your views here.
from meiduo_mall.libs.yuntongxun.sms import CCP
from celery_tasks.sms.tasks import send_sms_code

class SMSCodeView(APIView):
    def get(self, request, mobile):
        # 判断60s
        conn = get_redis_connection('verify')
        flag = conn.get('sms_flag_%s'%mobile)
        if flag:
            return Response({'message':'请求过于频繁'},status=400)
        # 生成短信验证码
        sms_code = '%06d'%randint(0,999999)
        # 保存短信验证码
        pl = conn.pipeline()
        # conn = get_redis_connection('verify')
        # 发送短信
        pl.setex('sms_%s'%mobile,300,sms_code)
        pl.setex('sms_flag_%s'%mobile,60,1)
        pl.execute()
        # ccp = CCP()
        # ccp.send_template_sms(mobile,[sms_code,'5'],1)
        send_sms_code.delay(mobile, sms_code)
        # 返回结果
        return Response({'message':'ok'})