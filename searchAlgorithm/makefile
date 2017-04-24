CC = g++
CFLAGS = -std=c++11 -g -I"./includes" -I"./jsoncpp/json" -Wextra `pkg-config --cflags --libs libmongoc-1.0`

LDFLAGS = -Wextra `pkg-config --cflags --libs libmongoc-1.0`


generate : main.o jsoncpp.o
	${CC} ${CFLAGS} main.o jsoncpp.o ${LDFLAGS} -o generate

jsoncpp.o : ./jsoncpp/jsoncpp.cpp ./jsoncpp/json/json.h ./jsoncpp/json/json-forwards.h
	${CC} ${CFLAGS} -c ./jsoncpp/jsoncpp.cpp

main.o : ./src/main.cpp
	${CC} ${CFLAGS} -c ./src/main.cpp

clean:
	rm *.o generate
