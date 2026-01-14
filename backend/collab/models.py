from django.db import models
from core.models import User, Profile
from django.utils import timezone


class CollaborativeDocument(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(default='')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    couple = models.OneToOneField(Profile, on_delete=models.SET_NULL, null=True, blank=True)  # 关联情侣关系
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class DocumentOperation(models.Model):
    """记录文档操作历史，用于冲突解决"""
    document = models.ForeignKey(CollaborativeDocument, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    operation_type = models.CharField(max_length=10, choices=[('insert', '插入'), ('delete', '删除')])
    position = models.IntegerField()
    text = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    revision = models.IntegerField(default=0)  # 操作版本号

    def to_operation(self):
        """转换为OT算法可用的Operation对象"""
        from App.ot import Operation
        return Operation(
            op_type=self.operation_type,
            position=self.position,
            text=self.text
        )