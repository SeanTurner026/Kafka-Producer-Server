import sys
from twisted.internet import ssl, reactor
from twisted.internet.address import IPv4Address
from twisted.internet.protocol import ClientFactory, Protocol
from OpenSSL.SSL import TLSv1_2_METHOD

sent_data = " ".join(sys.argv[1:])

class EchoClient(Protocol):
    def connectionMade(self):
        print("Connection established")
        self.transport.write(bytes(sent_data, "utf-8"))

    def dataReceived(self, data):
        print("Server said:", data)
        self.transport.loseConnection()

class EchoClientFactory(ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        reactor.stop()

if __name__ == '__main__':
    factory = EchoClientFactory()
    tls_options = ssl.DefaultOpenSSLContextFactory('domain.key',
                                                   'domain.crt',
                                                   sslmethod=TLSv1_2_METHOD)
    reactor.connectSSL('127.0.0.1', 8000, factory, tls_options)
    reactor.run()
