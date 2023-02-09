FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=swarm_server.prod
WORKDIR /backend
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv sync --system
COPY . .
RUN mkdir log
RUN python manage.py collectstatic --no-input