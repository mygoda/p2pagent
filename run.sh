#!/bin/bash
gunicorn -w 4 -b 0.0.0.0:5045 wsgi:app --log-file error.log
export C_FORCE_ROOT=true
celery worker -A api.celery --loglevel=info
