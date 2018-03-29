## Standalone TLS/SSL TCP server

The producer.py is an Apache Kafka producer server which listens on a given port from connections from a whitelisted set of IPs. The server produces each line recieved as a message on a given topic on the Kafka instance.

### producer.py:
- Communicates with a kafka server on 127.0.0.1 with port 9092
- Whitelists localhost (127.0.0.1)
- Listens to incoming communication on port 8000
- Utilises private key and self signed certificates called domain
- Anything separated by commas passed after -c will also be added to the whitelisted hosts.

### Run the kafka producer server with the following command.
```
python tcp_kafka_producer.py \
    -k localhost:9092 \
    -i 127.0.0.1 \
    -f domain.key,domain.crt \
    -p 8000 \
    -c <additional,ip,addresses>
```

### Send messages with the following command.
```
python echoserv_client.py test test
```