FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update \
    && apt-get -y upgrade

RUN apt-get install -y \
    openssh-server \
    g++ \
    cmake \
    git \
    npm \
    curl \
    wget

RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | apt-key add -
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.2.list

RUN apt-get -y update

RUN curl -sL https://deb.nodesource.com/setup_10.x | /bin/bash

#installing the mongoc dependencies and driver
RUN apt-get install -y \
    pkg-config \
    libssl-dev \
    libsasl2-dev \
    nodejs

RUN cd ~ \
    && wget https://github.com/mongodb/mongo-c-driver/releases/download/1.16.2/mongo-c-driver-1.16.2.tar.gz \
    && tar xzf mongo-c-driver-1.16.2.tar.gz \
    && cd mongo-c-driver-1.16.2 \
    && mkdir cmake-build \
    && cd cmake-build \
    && cmake -DENABLE_AUTOMATIC_INIT_AND_CLEANUP=OFF .. \
    && make install -j32 \
    && cd ~ \
    && rm mongo-c-driver-1.16.2.tar.gz \
    && rm -rf mongo-c-driver-1.16.2

#installing mongocxx driver - connects c++ to mongo
RUN cd ~ \
    && wget https://github.com/mongodb/mongo-cxx-driver/archive/r3.2.1.tar.gz \
    && tar -xzf r3.2.1.tar.gz \
    && cd mongo-cxx-driver-r3.2.1/build \
    && cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local .. \
    && make EP_mnmlstc_core -j32 \
    && make -j32 \
    && make install \
    && cd ~ \
    && rm r3.2.1.tar.gz \
    && rm -rf mongo-cxx-driver-r3.2.1

RUN apt-get install -y mongodb-org

RUN apt install -y python3 python3-pip

RUN pip3 install beautifulsoup4 pymongo lxml

COPY . /src

RUN cd /src/webserver \
  && npm install

RUN cd /src/searchAlgorithm \
  && make

RUN mkdir -p /data/db
RUN mongod & python3 /src/webserver/schools/Guelph/getClasses.py

EXPOSE 8083

WORKDIR /src/webserver

CMD mongod & npm start

