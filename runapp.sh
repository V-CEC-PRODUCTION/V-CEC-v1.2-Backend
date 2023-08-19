pip install -r requirements.txt &

# Start Celery Beat
celery -A your_project_name beat --loglevel=info &

# Start Celery worker
celery -A your_project_name worker --loglevel=info 