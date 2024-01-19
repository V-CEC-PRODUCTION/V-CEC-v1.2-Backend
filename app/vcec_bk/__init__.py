from .celery import app as celery_app
import sys

sys.dont_write_bytecode = True

__all__ = ("celery_app",)
