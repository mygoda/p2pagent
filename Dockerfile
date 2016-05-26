FROM ubuntu:latest
MAINTAINER xutaomac "tracy1303300@gmail.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install -y transmission-cli transmission-common transmission-daemon
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["api.py"]