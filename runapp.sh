celery -A vcec_bk beat --loglevel=info 

# Start Celery worker
celery -A vcec_bk worker --loglevel=info 

