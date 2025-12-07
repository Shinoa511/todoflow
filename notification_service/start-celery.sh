#!/usr/bin/env bash
# run celery worker
celery -A app.tasks.celery_app worker --loglevel=info
