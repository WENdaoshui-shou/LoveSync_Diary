from rest_framework import serializers
from .models import CommunityEvent, Report, ReportAction, ReportStatistics, ReportType


class CommunityEventSerializer(serializers.ModelSerializer):
    """社区活动序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_at_formatted = serializers.SerializerMethodField(read_only=True)
    start_date_formatted = serializers.SerializerMethodField(read_only=True)
    end_date_formatted = serializers.SerializerMethodField(read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CommunityEvent
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'image', 'image_url', 'start_date', 'start_date_formatted',
            'end_date', 'end_date_formatted', 'location', 'participant_count',
            'prize_info', 'is_pinned', 'created_at', 'created_at_formatted',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'participant_count']

    def get_created_at_formatted(self, obj):
        """格式化创建时间"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S') if obj.created_at else None

    def get_start_date_formatted(self, obj):
        """格式化开始时间"""
        return obj.start_date.strftime('%Y-%m-%d %H:%M:%S') if obj.start_date else None

    def get_end_date_formatted(self, obj):
        """格式化结束时间"""
        return obj.end_date.strftime('%Y-%m-%d %H:%M:%S') if obj.end_date else None

    def get_image_url(self, obj):
        """获取图片URL"""
        return obj.image.url if obj.image else None


class ReportTypeSerializer(serializers.ModelSerializer):
    """举报类型序列化器"""
    
    class Meta:
        model = ReportType
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ReportSerializer(serializers.ModelSerializer):
    """举报记录序列化器"""
    reporter_name = serializers.CharField(source='reporter.name', read_only=True)
    reporter_username = serializers.CharField(source='reporter.username', read_only=True)
    reported_user_name = serializers.CharField(source='reported_user.name', read_only=True)
    reported_user_username = serializers.CharField(source='reported_user.username', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    priority_display = serializers.SerializerMethodField(read_only=True)
    created_at_formatted = serializers.SerializerMethodField(read_only=True)
    reviewed_at_formatted = serializers.SerializerMethodField(read_only=True)
    resolved_at_formatted = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Report
        fields = [
            'id', 'reporter', 'reporter_name', 'reporter_username',
            'reported_user', 'reported_user_name', 'reported_user_username',
            'report_type', 'report_type_display', 'title', 'description',
            'evidence', 'status', 'status_display', 'content_type', 'content_id',
            'content_title', 'reviewed_by', 'reviewed_by_name', 'review_notes',
            'action_taken', 'priority', 'priority_display', 'is_urgent',
            'created_at', 'created_at_formatted', 'reviewed_at', 'reviewed_at_formatted',
            'resolved_at', 'resolved_at_formatted'
        ]
        read_only_fields = [
            'created_at', 'reviewed_at', 'resolved_at', 'reviewed_by',
            'action_taken', 'review_notes'
        ]

    def get_priority_display(self, obj):
        """获取优先级显示文本"""
        priority_map = {1: '低', 2: '中', 3: '高'}
        return priority_map.get(obj.priority, '未知')

    def get_created_at_formatted(self, obj):
        """格式化创建时间"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')

    def get_reviewed_at_formatted(self, obj):
        """格式化处理时间"""
        return obj.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if obj.reviewed_at else None

    def get_resolved_at_formatted(self, obj):
        """格式化解决时间"""
        return obj.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if obj.resolved_at else None

    def validate(self, data):
        """验证举报数据"""
        # 检查是否自己举报自己
        if data.get('reporter') and data.get('reported_user'):
            if data['reporter'] == data['reported_user']:
                raise serializers.ValidationError('不能举报自己')
        
        # 检查标题和描述
        if not data.get('title', '').strip():
            raise serializers.ValidationError('举报标题不能为空')
        
        if not data.get('description', '').strip():
            raise serializers.ValidationError('举报描述不能为空')
        
        return data


class ReportActionSerializer(serializers.ModelSerializer):
    """举报处理措施序列化器"""
    report_title = serializers.CharField(source='report.title', read_only=True)
    executed_by_name = serializers.CharField(source='executed_by.name', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    created_at_formatted = serializers.SerializerMethodField(read_only=True)
    executed_at_formatted = serializers.SerializerMethodField(read_only=True)
    expires_at_formatted = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReportAction
        fields = [
            'id', 'report', 'report_title', 'action_type', 'action_type_display',
            'description', 'duration', 'executed_by', 'executed_by_name',
            'created_at', 'created_at_formatted', 'executed_at', 'executed_at_formatted',
            'expires_at', 'expires_at_formatted', 'is_executed', 'is_reverted'
        ]
        read_only_fields = ['created_at', 'executed_at', 'expires_at']

    def get_created_at_formatted(self, obj):
        """格式化创建时间"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')

    def get_executed_at_formatted(self, obj):
        """格式化执行时间"""
        return obj.executed_at.strftime('%Y-%m-%d %H:%M:%S') if obj.executed_at else None

    def get_expires_at_formatted(self, obj):
        """格式化过期时间"""
        return obj.expires_at.strftime('%Y-%m-%d %H:%M:%S') if obj.expires_at else None

    def validate(self, data):
        """验证处理措施数据"""
        action_type = data.get('action_type')
        duration = data.get('duration')
        
        # 验证持续时间
        if action_type in ['account_suspension', 'account_ban']:
            if not duration or duration <= 0:
                raise serializers.ValidationError('账号暂停或封禁需要设置持续时间')
        
        return data


class ReportStatisticsSerializer(serializers.ModelSerializer):
    """举报统计序列化器"""

    class Meta:
        model = ReportStatistics
        fields = [
            'id', 'date', 'total_reports', 'pending_reports', 'resolved_reports',
            'dismissed_reports', 'content_reports', 'harassment_reports',
            'spam_reports', 'other_reports', 'avg_resolution_time', 'resolution_rate'
        ]
        read_only_fields = ['date']


class ReportListSerializer(serializers.ModelSerializer):
    """举报列表序列化器（简化版）"""
    reporter_name = serializers.CharField(source='reporter.name', read_only=True)
    reported_user_name = serializers.CharField(source='reported_user.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    priority_display = serializers.SerializerMethodField(read_only=True)
    created_at_formatted = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Report
        fields = [
            'id', 'reporter_name', 'reported_user_name', 'report_type',
            'report_type_display', 'title', 'status', 'status_display',
            'priority', 'priority_display', 'is_urgent', 'created_at_formatted'
        ]

    def get_priority_display(self, obj):
        """获取优先级显示文本"""
        priority_map = {1: '低', 2: '中', 3: '高'}
        return priority_map.get(obj.priority, '未知')

    def get_created_at_formatted(self, obj):
        """格式化创建时间"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')