from django.shortcuts import render
from rest_framework.views import APIView
from users.models import User
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from users.serializers import UserSerializers


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

    def post(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid()
        print(ser.errors)
        response = super().post(request)
        return response
