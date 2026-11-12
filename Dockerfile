FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/reference_registry/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


#FROM python:3.13
#
#ENV PYTHONUNBUFFERED 1
#
#COPY requirements.txt /opt/reference_registry/
#WORKDIR /opt/reference_registry/
#
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY . /opt/reference_registry/
