pip install -r requirements.txt &

# Start Celery Beat
celery -A vcec_bk beat --loglevel=info &

# Start Celery worker
celery -A vcec_bk worker --loglevel=info &

python3.11.4 manage.py runserver