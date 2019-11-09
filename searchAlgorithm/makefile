CC = g++
CFLAGS = -std=c++11 -g -I"./includes" -I"./mrc" -I"./jsoncpp/json" -Wextra `pkg-config --cflags --libs libmongocxx`

LDFLAGS = -Wextra -DMONGOCXX_STATIC `pkg-config --cflags --libs libmongocxx` -Wl,-rpath,/usr/local/lib

generate : main.o jsoncpp.o mcr.o
	${CC} ${CFLAGS} main.o jsoncpp.o mcr.o  ${LDFLAGS} -o generate

jsoncpp.o : ./jsoncpp/jsoncpp.cpp ./jsoncpp/json/json.h ./jsoncpp/json/json-forwards.h
	${CC} ${CFLAGS} -c ./jsoncpp/jsoncpp.cpp

mcr.o : ./mcr/mcr.cpp
	${CC} ${CFLAGS} -c ./mcr/mcr.cpp

main.o : ./src/main.cpp
	${CC} ${CFLAGS} -c ./src/main.cpp -g

clean:
	rm *.o generate
