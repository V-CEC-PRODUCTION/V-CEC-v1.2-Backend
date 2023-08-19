export REDIS_URL="rediss://red-cjg3hhk1ja0c739uk8q0:lHFFzjpghpw27zyVujLlv9YqWf5kTujR@singapore-redis.render.com:6379" &


export DATABASE_URL=postgres://superadmin:SinPVZCts4G3PwzqhsrAaQh6FvTJ4hae@dpg-cjafqelm2m9c73d70hcg-a.singapore-postgres.render.com/vcec_1 &

export EMAIL_PASSWORD="VvUDbYBCFQKINgrz" &

#rm -rf celery
# Start Celery Beat
celery -A vcec_bk beat --loglevel=info &

# Start Celery worker
celery -A vcec_bk worker --loglevel=info &

python3.11.4 manage.py runserver