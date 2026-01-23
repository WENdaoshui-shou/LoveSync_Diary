from rest_framework import serializers
from .models import VIPMember, VIPPrivilege, VIPOrder

class VIPMemberSerializer(serializers.ModelSerializer):
    """VIP会员序列化器"""
    class Meta:
        model = VIPMember
        fields = '__all__'

class VIPPrivilegeSerializer(serializers.ModelSerializer):
    """VIP特权序列化器"""
    class Meta:
        model = VIPPrivilege
        fields = '__all__'

class VIPOrderSerializer(serializers.ModelSerializer):
    """VIP订单序列化器"""
    class Meta:
        model = VIPOrder
        fields = '__all__'