FROM python:3.8
RUN apt update
RUN apt install -y socat
RUN mkdir /server
COPY flag.txt /server
COPY graph.py /server
COPY public_key.json /server
COPY server.py /server
COPY server.sh /server
RUN chmod +x /server/server.sh
WORKDIR /server
EXPOSE 3000
CMD ./server.sh