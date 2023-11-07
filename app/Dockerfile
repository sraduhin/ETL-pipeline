FROM python:3.10

WORKDIR /opt/app
ENV DJANGO_SETTING_MODULE 'config.settings'

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

COPY uwsgi/uwsgi.ini uwsgi.ini
COPY docker-entrypoint.sh /usr/bin
COPY supervisor.conf /usr/local/etc/supervisord.conf

ENTRYPOINT ["supervisord"]
#CMD python3 manage.py runserver
#CMD ["supervisord"]
# work & not bad
#RUN chmod +x /usr/bin/docker-entrypoint.sh
#ENTRYPOINT ["/usr/bin/docker-entrypoint.sh"]

# work & good
#CMD python3 manage.py collectstatic --no-input && \
#    python3 manage.py migrate && \
#    uwsgi --strict --ini uwsgi.ini