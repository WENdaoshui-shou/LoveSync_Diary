"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LoveSync.settings')
    
    if len(sys.argv) > 1 and sys.argv[1] in ['migrate', 'createsuperuser', 'shell', 'collectstatic']:
        # 对于管理命令，使用标准的 Django 管理接口
        execute_from_command_line(sys.argv)
    elif len(sys.argv) == 1:
        # 如果没有参数，启动 Daphne 服务器
        django.setup()
        print("Starting Daphne server on http://127.0.0.1:8000/")
        print("Daphne can handle both HTTP and WebSocket requests")
        # 使用 subprocess 运行 daphne 命令
        daphne_args = ["daphne", "-b", "0.0.0.0", "-p", "8000", "LoveSync.asgi:application"]
        subprocess.run(daphne_args)
    else:
        # 对于其他命令，使用标准的 Django 管理接口
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
