FROM python:3.7

RUN mkdir -p /project
RUN pip config set global.trusted-host mirrors.aliyun.com
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple
RUN pip install pip -U
RUN pip install django==3.0 APScheduler==3.6.3 django-apscheduler==0.3.0

WORKDIR /project