from rest_framework import serializers
from .models import CommunityEvent


class CommunityEventSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    class Meta:
        model = CommunityEvent
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'image', 'image_url', 'start_date', 'end_date', 'location',
            'participant_count', 'prize_info', 'is_pinned',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_status(self, value):
        valid_statuses = ['active', 'upcoming', 'ended']
        if value not in valid_statuses:
            raise serializers.ValidationError(f'无效的活动状态。可选值: {valid_statuses}')
        return value
