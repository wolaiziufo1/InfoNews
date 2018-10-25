import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        # 'user': UserSerializer(user, context={'request': request}).data
        'username': user.username,
        'user_id':user.id,
    }


class UsernameMobileAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断username的数据形式
        try:
            if re.match(r'1[3-9]\d{9}$',username):
                user=User.objects.get(mobile=username)
            else:
                # 不符合手机格式 用username查询
                user = User.objects.get(username=username)
        except:
            user = None

        if user is not None and user.check_password(password):
            return user

