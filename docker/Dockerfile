FROM python:3.10

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR opt/app

RUN pip install --upgrade pip

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./local/uwsgi/uwsgi.ini /uwsgi.ini
COPY ./local/django/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./local/django/celery.sh celery.sh
RUN chmod +x celery.sh
#COPY docker-entrypoint.sh.sh /usr/bin

#CMD python3 manage.py runserver
#CMD ["supervisord"]
# work & not bad
#RUN chmod +x /usr/bin/docker-entrypoint.sh.sh
#ENTRYPOINT ["/usr/bin/docker-entrypoint.sh.sh"]

# work & good
#CMD python3 manage.py collectstatic --no-input && \
#    python3 manage.py migrate && \
#    uwsgi --strict --ini uwsgi.ini


