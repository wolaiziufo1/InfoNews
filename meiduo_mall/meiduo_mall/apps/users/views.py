from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from users.models import User
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, GenericAPIView
from users.serializers import UserSerializers, UserDeailSerializer, UserEmailViewSerializer
from itsdangerous import TimedJSONWebSignatureSerializer as TJS


# Create your views here.
class UserNameCountView(APIView):
    def get(self, request, username):
        # 查询用户数量
        count = User.objects.filter(username=username).count()
        return Response(
            {
                'count': count,
            }
        )


class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return Response(
            {
                'count': count,
            }
        )


class UserView(CreateAPIView):
    serializer_class = UserSerializers

    # def post(self, request, *args, **kwargs):
    #     ser = self.get_serializer(data=request.data)
    #     ser.is_valid()
    #     print(ser.errors)
    #     response = super().post(request)
    #     return response


class UserDetailView(RetrieveAPIView):
    serializer_class = UserDeailSerializer

    def get_object(self):
        return self.request.user


class UserEmailView(UpdateAPIView):
    serializer_class = UserEmailViewSerializer

    def get_object(self):
        return self.request.user


class EmailVerifyView(GenericAPIView):
    def get(self, request):
        # 获取前端数据
        data = request.query_params.get('token')
        if data is None:
            return Response({'errors': '缺少token值'}, status=400)
        # 解密
        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(data)
        except:
            return Response({'errors': '无效的token值'}, status=400)
        # 查询用户
        username = data.get('username')
        user = User.objects.get(username=username)
        user.emial_activate = True
        user.save()
        ser = UserDeailSerializer(user)
        # 邮箱状态更新
        # return Response('username', 'email', 'email_activate')
        return Response(ser.data)