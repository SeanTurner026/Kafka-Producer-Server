import sys
import argparse
from twisted.internet import ssl, reactor
from twisted.internet.protocol import Factory, Protocol
from OpenSSL.SSL import TLSv1_2_METHOD
from confluent_kafka import Producer

parser = argparse.ArgumentParser(description='Kafka TCP Stream Forwarder')

parser.add_argument('-k', '--kafka', metavar='KAFKA',
                    help='Kafka host:ip to forward to')

parser.add_argument('-t', '--topic', metavar='TOPIC',
                    help='Topic for messages')

parser.add_argument('-i', '--interface', metavar='INTERFACE',
                    help='Listen on this interface')

parser.add_argument('-p', '--port', metavar='PORT',
                    help='Listen for client connections on this port')

parser.add_argument('-c', '--client', metavar='IP',
                    help='Add additional IP host addresses or CIDR addresses \
                    to approved clients <format>: (host2,host3,host4)')

parser.add_argument('-f', '--cert', metavar='FILENAME',
                    help='Certificate for server <format>: domain1.key,domain1.crt')

                    # unused
parser.add_argument('-m', '--management', metavar='TOPIC',
                    help='Topic for connection events')

                    # unused
parser.add_argument('--info', dest=' ', help='More logging to console')

                    # unused
parser.add_argument('--debug', dest=' ', help='Most detailed logging to \
                    console')

# creates a dictionary to hold all information called with the program
args = vars(parser.parse_args())

# initialise listening port
port = int(args['port'])

# initialise variable for kafka address
kafka_client = args['kafka']

# initialise host to listen for
if args['client'] == None:
    host_addrs = [args['interface']]

# initialise additional IP hosts to listen for
else:
    host_addrs = args['client'].split(',')
    host_addrs.append(args['interface'])

# initialise list of list of key and certificates to accompany hosts
keys = args['cert'].split(',')

# initialise topic for kafka producer
topic = args['topic']

# unused, code to cause program to print diagnostic information to console if
# proper flags are passed when calling the program
# if '--debug' in sys.argv[1:]:
#     pass
# elif '--info' in sys.argv[1:]:
#     pass


class Echo(Protocol):
    def dataReceived(self, data):
        """send response to client, and produce data to kafka consumer"""
        # extract IP address from incoming connection
        addr, _ = self.transport.client
        # confirm that cleint's IP is a whitelisted host
        if addr in host_addrs:
            # send confirmation message to client
            self.transport.write(b'received!')
            # connect to kafka
            p = Producer({'bootstrap.servers': kafka_client})
            # stage data from clent to kafka topic
            p.produce(topic, data)
            # send all data to kafka topic
            p.flush()
            print('sent message to kafka!')

if __name__ == '__main__':
    # factory produces the echo protocol, which handles input on the incoming
    # server connection
    factory = Factory()
    factory.protocol = Echo

    # initialise listening on given port with given credentials
    # keys[0] - domain.key, keys[1] - domain.crt
    reactor.listenSSL(port,
                      factory,
                      ssl.DefaultOpenSSLContextFactory(keys[0],
                                                       keys[1],
                                                       sslmethod=TLSv1_2_METHOD),
                    )
                        # # the interface argument of listenSSL takes an IP
                        # # address, however, I am not able to get my program
                        # # to run with an IP address other than localhost or
                        # # the host computer's IP

                        # interface='192.168.1.109')
    # starts the event loop that Twisted utilises, and provides threading
    reactor.run()
