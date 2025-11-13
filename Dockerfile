FROM python:3.12
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /www && \
    mkdir /www/src \
    mkdir /www/src/static
WORKDIR /www/src
COPY ./requirements.txt .

RUN pip config set global.trusted-host "pypi.org files.pythonhosted.org"
RUN python -m pip install --upgrade "pip>=25.0"
# --no-cache-dir
RUN pip install -r requirements.txt
COPY . .
RUN rm -rf wink/migrations && \
    mkdir wink/migrations
COPY wink/__init__.py wink/migrations/__init__.py
