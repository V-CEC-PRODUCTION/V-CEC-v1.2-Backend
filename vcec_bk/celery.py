import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vcec_bk.settings")

app = Celery("vcec_bk")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()