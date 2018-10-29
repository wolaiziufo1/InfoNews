import re

from django_redis import get_redis_connection
from rest_framework import serializers
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from django.conf import settings
from rest_framework_jwt.settings import api_settings

from oauth.models import OAuthQQUser
from users.models import User


class QQAuthUserSerializer(serializers.ModelSerializer):
    # 显示指明字段,不是模型类字段
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    access_token = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('password', 'mobile', 'sms_code', 'access_token', 'username', 'token')
        read_only_field = ('username',)
        extra_kwargs = {
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True,
                'error_messages': {
                    'max_length': '密码过长'
                }
            },
            'mobile': {
                'max_length': 11,
                'min_length': 11,
                'error_messages': {
                    'max_length': '密码过长'
                }
            },
            'username': {
                'max_length': 11,
                'min_length': 11,
                'error_messages': {
                    'max_length': '密码过长'
                }
            },
        }

    # 手机号验证
    def validate_mobile(self, value):
        # 匹配手机号格式
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式不正确')
        return value

    def validate(self, attrs):
        # access_token验证
        # 解密access_token
        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(attrs['access_token'])
        except:
            raise serializers.ValidationError('错误的access_token值')
        openid = data.get('openid')
        # attrs添加额外属性 方便保存数据时进行提取
        attrs['openid'] = openid
        # 短信验证
        # 从redis中获取真实短信
        # 1.建立连接
        conn = get_redis_connection('verify')
        # 2.获取数据
        real_sms_code = conn.get('sms_%s' % attrs['mobile'])
        if not real_sms_code:
            raise serializers.ValidationError('短信失效')
        # 3.转换数据
        real_sms_code = real_sms_code.decode()
        # 4.比对验证
        if attrs['access_token'] != real_sms_code:
            raise serializers.ValidationError('短信错误')
        # 验证用户
        try:
            user = User.objects.get(mobile=attrs['mobile'])
        except:
            return attrs
        else:
            # 校验密码
            if user.check_password(attrs['password']):
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('密码错误')

    def create(self, validated_data):
        # 获取user数据判断用户是否注册
        user = validated_data.get('user', None)
        if user is None:
            # 用户未注册 注册新用户
            user = User.objects.create_user(username=validated_data['mobile'], password=validated_data['password']
                                            , mobile=validated_data['mobile'])
        # 用户注册过,绑定用户
        OAuthQQUser.objects.create(user=user, openid=validated_data['openid'])
        # 生成jwt token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # 对user对象添加token属性字段
        user.token = token
        return user
