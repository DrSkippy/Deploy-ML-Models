FROM python:3.10.9
RUN apt update && apt upgrade -y

ENV APP /model
RUN mkdir $APP
WORKDIR $APP

RUN apt install make curl -y
RUN pip install --upgrade pip

# get and install poetry package manager
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH /root/.local/bin:$PATH
# set poetry so it does not use a virtual environment in deployment container
RUN poetry config virtualenvs.create false

ENV PYTHONPATH $APP
COPY ./pyproject.toml ./poetry.lock $APP/
RUN poetry install --only main

COPY ./model $APP/

ENTRYPOINT poetry run uwsgi --ini model_serve.ini