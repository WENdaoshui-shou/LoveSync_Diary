from django.db import models
from core.models import User


class Photo(models.Model):
    """照片模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/%Y/%m/%d/')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo by {self.user.username} at {self.uploaded_at}"

    class Meta:
        ordering = ['-uploaded_at']