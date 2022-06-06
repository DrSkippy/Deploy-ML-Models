FROM python:3.8.12
RUN apt update && apt upgrade -y

ENV APP /model
RUN mkdir $APP
WORKDIR $APP

RUN apt install make curl -y
RUN pip install --upgrade pip

# get and install poetry package manager
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH /root/.poetry/bin:$PATH
# set poetry so it does not use a virtual environment in deployment container
RUN poetry config virtualenvs.create false

ENV PYTHONPATH $APP
COPY ./pyproject.toml ./poetry.lock $APP/
RUN poetry install --no-dev

COPY ./model $APP/
RUN mkdir ./data
COPY ./data /data

ENTRYPOINT poetry run uwsgi --ini model_serve.ini