from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "email_client.settings")

app = Celery("email_client")

# Load task modules from all registered Django apps
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["email_tasks"])

app.conf.beat_schedule = {
    "check-email-every-1-minute": {
        "task": "email_tasks.tasks.check_emails",
        "schedule": crontab(minute="*/1"),  # Run every 1 minute
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
