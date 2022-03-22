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
RUN apt-get update
RUN apt-get install -y iputils-ping
RUN apt-get install -y net-tools
RUN apt-get install -y tcpdump
RUN npm install -g ssb-server
EXPOSE 8008/tcp
EXPOSE 8008/udp
COPY . /app

ENTRYPOINT ["ssb-server", "start","--host","0.0.0.0"]
CMD []