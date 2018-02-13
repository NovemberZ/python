from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from player import PlayerServer
from handler import PlayerServerHandler

import logging
import argparse


ap = argparse.ArgumentParser()
ap.add_argument("-p", "--port", required=True,
                help="thrift server port")
args = vars(ap.parse_args())

port = args['port']

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s  %(filename)s [%(levelname)s]  %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('starting app...')

    handler = PlayerServerHandler()
    processor = PlayerServer.Processor(handler)
    transport = TSocket.TServerSocket('127.0.0.1', port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    logging.info("Starting thrift server, listen port: %s", port)
    server.serve()

    logging.info("exit!")
