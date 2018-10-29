from django.shortcuts import render
from QQLoginTool.QQtool import OAuthQQ
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJS

from oauth.serializers import QQAuthUserSerializer
from .models import OAuthQQUser


# Create your views here.

class QQAuthURLView(APIView):
    def get(self, request):
        # 获取前端传递数据
        state = request.query_params.get('state')

        if not state:
            state = '/'

        # 构造qq登陆的跳转连接
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=state)
        login_url = oauth.get_qq_url()

        # 返回结果
        return Response({'login_url': login_url})


class QQAuthUserView(CreateAPIView):
    serializer_class = QQAuthUserSerializer
    def get(self, request):
        # 获取code值
        code = request.query_params.get('code', None)
        # 判断code值是否存在
        if not code:
            return Response({'errors': '缺少code值'},status=400)
        # 生成qq对象
        state = '/'
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=state)
        # 通过code值获取assess_token
        access_token = oauth.get_access_token(code)
        # 通过assess_token值获取openid
        openid = oauth.get_open_id(access_token)
        # 判断openid是否绑定美多对象
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except:
            # openid未绑定用户
            # return Response({'errors': '缺少code值'}, status=400)
            # openid加密
            tjs = TJS(settings.SECRET_KEY, 300)
            open_id = tjs.dumps({'openid': openid}).decode()
            return Response({'access_token': open_id})
        else:
            # 已经绑定过用户
            # 登陆成功
            # 获取用户对象
            user = qq_user.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            # 对user对象添加token属性字段
            user.token = token
            return Response(
                {
                    'token': token,
                    'username': user.username,
                    'user_id': user.id
                }
            )
