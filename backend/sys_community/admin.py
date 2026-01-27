from django.contrib import admin
from .models import CommunityEvent


@admin.register(CommunityEvent)
class CommunityEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'is_pinned', 'participant_count', 'created_at']
    list_filter = ['status', 'is_pinned', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-is_pinned', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'status', 'is_pinned')
        }),
        ('详细信息', {
            'fields': ('image_url', 'start_date', 'end_date', 'location', 'prize_info')
        }),
        ('统计信息', {
            'fields': ('participant_count',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
