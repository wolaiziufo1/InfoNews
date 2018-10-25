import re

from rest_framework import serializers
from users.models import User
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings


class UserSerializers(serializers.ModelSerializer):
    # 显示指明字段
    sms_code = serializers.CharField(max_length=6, write_only=True)
    password2 = serializers.CharField(max_length=20, min_length=8, write_only=True)
    allow = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'sms_code',
                  'password2', 'allow', 'password', 'token')
        extra_kwargs = {
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True,
                'error_messages': {
                    'max_length': '密码过长'
                }
            },
            'username': {
                'max_length': 20,
                'min_length': 5,
                'error_messages': {
                    'max_length': '密码过长'
                }
            }
        }

    # 手机号验证
    def validate_mobile(self, value):

        # 匹配手机号格式
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式不正确')
        return value

    # 验证同意协议
    def validate_allow(self, value):
        if value != 'true':
            raise serializers.ValidationError('协议未同意')
        return value

    def validate(self, attrs):
        # 密码验证
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('密码不一致')

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
        if attrs['sms_code'] != real_sms_code:
            raise serializers.ValidationError('短信错误')

        return attrs

    def create(self, validated_data):
        del validated_data['sms_code']
        del validated_data['password2']
        del validated_data['allow']

        # user = super().create(validated_data)
        # 密码加密
        # user.set_password(validated_data['password'])
        # user.save()
        # 管理器方法保存用户
        user = User.objects.create_user(username=validated_data['username'],
                                        mobile=validated_data['mobile'],
                                        password=validated_data['password'])
        # 生成jwt token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # 对user对象添加token属性字段
        user.token = token
        return user
