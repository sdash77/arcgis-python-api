from arcgis.gis import *
from arcgis.features import *

import six
from six.moves.urllib_parse import urlencode


class StreamLayer(Layer):
    # autobahn, twisted, pyOpenssl, service_identity
    def __init__(self, url, gis=None):
        super(StreamLayer, self).__init__(url, gis)
        self._streamtoken = self.properties.streamUrls[0].token
        self._streamurl = self.properties.streamUrls[0].urls[0]
        self._out_sr = self.properties.spatialReference.wkid
        self.filter = {}
        self._on_features = None
        self._on_disconnect = None
        self._on_error = None

    @property
    def out_sr(self):
        """The spatial reference of the streamed features"""
        return self._out_sr

    @out_sr.setter
    def out_sr(self, value):
        self._out_sr = value

    @property
    def filter(self):
        """
        Property used for filtering the streamed features so they meet spatial and SQL like criteria,
        and return the specified fields
        """
        return self._filter

    @filter.setter
    def filter(self, value):
        self._filter = value

    def subscribe(self, on_features, on_open=None, on_disconnect=None, on_error=None):
        try:
            import sys
            import ssl
            from twisted.internet import reactor
            from twisted.python import log

            from autobahn.twisted.websocket import WebSocketClientFactory, \
                WebSocketClientProtocol, connectWS
        except:
            print('Install autobahn, twisted, pyOpenssl, service_identity packages to subscribe')

        url = self._streamurl

        params = {"token": self._streamtoken}
        params.update(self.filter)

        if self.out_sr != self.properties.spatialReference.wkid:
            params['outSR'] = self.out_sr

        url = "{url}/subscribe?{params}".format(url=url, params=urlencode(params))

        class StreamServiceClientProtocol(WebSocketClientProtocol):
            def onOpen(self):
                if on_open is not None:
                    on_open()

            def onMessage(self, payload, isBinary):
                if isBinary:
                    print("Binary message received: {0} bytes".format(len(payload)))
                else:
                    msg = format(payload.decode('utf8'))
                    on_features(msg)

        factory = WebSocketClientFactory(url, headers={'token': self._streamtoken})

        factory.protocol = StreamServiceClientProtocol
        connectWS(factory)

        reactor.run()
