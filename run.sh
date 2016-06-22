#!/bin/bash
gunicorn -w 4 -b 0.0.0.0:5046 wsgi:app --log-file error.log&

export C_FORCE_ROOT=true
celery worker -A api.celery -w 4 --loglevel=info
