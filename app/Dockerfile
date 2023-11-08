FROM python:3.10

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./local/uwsgi/uwsgi.ini uwsgi.ini

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