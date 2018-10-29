from rest_framework import serializers
from areas.models import Area
from users.models import Address

class AreaSerializer(serializers.ModelSerializer):
    """
    行政规划
    """

    class Meta:
        model = Area
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(label='省', read_only=True)
    city = serializers.StringRelatedField(label='市', read_only=True)
    district = serializers.StringRelatedField(label='区', read_only=True)
    province_id = serializers.IntegerField(write_only=True)
    city_id = serializers.IntegerField(write_only=True)
    district_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Address
        # fields='__all__'
        exclude = ('user',)

    def create(self, validated_data):
        print(1111)
        # 获取用户对象
        user = self.context['request'].user

        validated_data['user'] = user
        # 调用父类方法，进行保存
        user = super().create(validated_data)

        return user