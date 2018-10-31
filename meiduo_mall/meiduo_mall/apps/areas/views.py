from django.shortcuts import render
from rest_framework.generics import ListAPIView,CreateAPIView,UpdateAPIView,ListAPIView
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from areas.models import Area


# Create your views here.
from areas.serializers import AreaSerializer, AddressSerializer
from users.models import Address


class AreaView(CacheResponseMixin,ListAPIView):
    queryset = Area.objects.filter(parent=None)
    serializer_class = AreaSerializer


class AreasView(CacheResponseMixin,ListAPIView):
    # 指定查询集,获取所有省的信息
    queryset = Area.objects.filter(parent=None)
    # 指定序列化器
    serializer_class = AreaSerializer
    # @cache_response(timeout=,cache=)

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Area.objects.filter(parent_id=pk)


class AddressView(CreateAPIView,UpdateAPIView,ListAPIView):
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter()

    def delete(self, request, pk):
        address = Address.objects.get(id=pk)
        address.is_deleted = True
        address.save()
        return Response({'message':'ok'})