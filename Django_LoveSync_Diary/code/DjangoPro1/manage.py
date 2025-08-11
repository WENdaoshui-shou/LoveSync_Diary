"""Django's command-line utility for administrative tasks."""
import logging
import os
import sys
import django
from daphne.cli import CommandLineInterface
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', )
logger = logging.getLogger(__name__)

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoPro1.settings')
    logger.info("Starting development server at http://127.0.0.1:8000/")
    try:
        if len(sys.argv) > 1 and sys.argv[1] in ['migrate', 'createsuperuser', 'shell', 'admin']:
            from django.core.management import execute_from_command_line
            execute_from_command_line(sys.argv)
        else:
            # 默认启动 Daphne 服务器
            django.setup()
            print("Starting Daphne server...")
            cli = CommandLineInterface()
            try:
                cli.run(["DjangoPro1.asgi:application"])
            except KeyboardInterrupt:
                print("\nServer stopped successfully")
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc


if __name__ == '__main__':
    main()
