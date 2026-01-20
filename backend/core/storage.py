import os
import oss2
from django.core.files.storage import Storage
from django.conf import settings


class AliyunOSSStorage(Storage):
    """阿里云OSS存储后端"""
    
    def __init__(self):
        self.access_key_id = os.environ.get('ALIYUN_OSS_ACCESS_KEY_ID')
        self.access_key_secret = os.environ.get('ALIYUN_OSS_ACCESS_KEY_SECRET')
        self.bucket_name = os.environ.get('ALIYUN_OSS_BUCKET_NAME', 'wendaoshuishou')
        self.endpoint = os.environ.get('ALIYUN_OSS_ENDPOINT', 'oss-cn-chengdu.aliyuncs.com')
        
        # 初始化OSS客户端
        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
    
    def _open(self, name, mode='rb'):
        """打开文件"""
        # 统一路径分隔符为正斜杠
        name = name.replace('\\', '/')
        
        # 从OSS下载文件到本地临时文件
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            self.bucket.get_object_to_file(name, temp_file.name)
            temp_file.close()
            return open(temp_file.name, mode)
        except Exception as e:
            temp_file.close()
            os.unlink(temp_file.name)
            raise
    
    def _save(self, name, content):
        """保存文件到OSS"""
        # 确保文件指针在开始位置
        content.seek(0)
        
        # 统一路径分隔符为正斜杠
        name = name.replace('\\', '/')
        
        # 上传文件到OSS
        self.bucket.put_object(name, content)
        
        return name
    
    def delete(self, name):
        """删除文件"""
        try:
            # 统一路径分隔符为正斜杠
            name = name.replace('\\', '/')
            self.bucket.delete_object(name)
        except oss2.exceptions.NoSuchKey:
            pass
    
    def exists(self, name):
        """检查文件是否存在"""
        try:
            # 统一路径分隔符为正斜杠
            name = name.replace('\\', '/')
            self.bucket.head_object(name)
            return True
        except oss2.exceptions.NoSuchKey:
            return False
    
    def url(self, name):
        """获取文件URL"""
        # 统一路径分隔符为正斜杠
        name = name.replace('\\', '/')
        # 直接返回 OSS 公共访问 URL
        return f"https://{self.bucket_name}.{self.endpoint}/{name}"
    
    def get_available_name(self, name, max_length=None):
        """获取可用的文件名"""
        # 避免文件名冲突
        if self.exists(name):
            # 生成唯一文件名
            import uuid
            ext = os.path.splitext(name)[1]
            name = os.path.splitext(name)[0]
            name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        return name
    
    def size(self, name):
        """获取文件大小"""
        try:
            # 统一路径分隔符为正斜杠
            name = name.replace('\\', '/')
            result = self.bucket.head_object(name)
            return int(result.headers['Content-Length'])
        except oss2.exceptions.NoSuchKey:
            raise FileNotFoundError(f"File not found: {name}")