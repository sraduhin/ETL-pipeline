FROM python:3.10

WORKDIR /opt/app
ENV DJANGO_SETTING_MODULE 'config.settings'

COPY requirements.txt requirements.txt
COPY uwsgi/uwsgi.ini uwsgi.ini

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
#    && apt-get update && apt-get install -y cron

COPY . .

CMD python3 manage.py collectstatic --no-input && \
    python3 manage.py migrate && \
    uwsgi --strict --ini uwsgi.ini