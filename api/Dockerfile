FROM python:3.8

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /eqar_db
WORKDIR /eqar_db

RUN pip install --upgrade pip
RUN apt-get update
RUN apt-get install -y build-essential python3-dev libldap2-dev libsasl2-dev

ADD requirements.txt /eqar_db/

RUN pip install -r requirements.txt

ADD . /eqar_db

CMD bash -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"

