import os

from celery import Celery

import sys

sys.dont_write_bytecode = True

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vcec_bk.settings")

app = Celery("vcec_bk")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
