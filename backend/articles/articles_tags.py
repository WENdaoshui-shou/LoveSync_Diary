from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.simple_tag
def get_content_type_id(obj):
    """获取对象或模型的内容类型ID"""
    content_type = ContentType.objects.get_for_model(obj)
    return content_type.id

@register.simple_tag
def get_comment_content_type():
    """获取评论的内容类型ID"""
    from .models import ColumnComment
    content_type = ContentType.objects.get_for_model(ColumnComment)
    return content_type.id