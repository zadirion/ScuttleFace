FROM ubuntu:focal
RUN apt-get update
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN apt-get -y install git
RUN pip install git+https://github.com/zadirion/facebook-scraper.git
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get install -qqy nodejs
RUN apt update
RUN apt-get install -qqy npm
RUN npm install -g ssb-server
EXPOSE 8008/tcp
EXPOSE 8008/udp
COPY . /app
#VOLUME /mnt/d/lmrepo /mnt/c
RUN cd /app
ENTRYPOINT ["python3", "/app/main.py"]
CMD []