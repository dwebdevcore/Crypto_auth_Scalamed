FROM python:3.6-alpine

WORKDIR /usr/src/app

RUN apk update

# For compiling anything in C/C++; including Cython
RUN apk add build-base

# For install cffi, a dependency of bcrypt:
RUN apk add libffi-dev openssl-dev

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./scalamed/ .
RUN touch db.sqlite3
RUN ./manage makemigrations
RUN ./manage migrate
ENTRYPOINT ["python3"]
CMD ["/usr/src/app/manage", "runserver", "0.0.0.0:80"]
