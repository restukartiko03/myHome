release: echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'pass')" | python manage.py shell
web: gunicorn myHome.wsgi --log-file -
