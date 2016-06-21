export C_FORCE_ROOT=true
celery worker -A api.celery --loglevel=info
