FROM python:3.8-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN mkdir /eqar_db
WORKDIR /eqar_db

RUN pip install --upgrade pip
RUN apt-get update && \
	apt-get install -y build-essential python3-dev libldap2-dev libsasl2-dev default-libmysqlclient-dev && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD requirements.txt /eqar_db/

RUN pip install -r requirements.txt

ADD . /eqar_db

RUN mkdir -p /eqar_db/static

CMD [ "/bin/bash", "-c", "python manage.py collectstatic --noinput && python manage.py wait_for_database && python manage.py migrate --fake-initial && gunicorn eqar_db.wsgi" ]
