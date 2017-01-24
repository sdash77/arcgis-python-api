"""
class Server

  - users
      - add/remove/update
      - roles
      - privileges

  - content (catalog tree)
      - add/get/list/search services
      - folders and permissions

      - Service
        - start, stop, rename, delete, edit
        - extensions (SOEs)

  - datastores

  - usage()

  - logs, kml, info

  - config
      - config store
      - properties
      - directories
"""
class Users(object):
    """
    Represents the basic operations that can be performed on
    a server using the REST API
    """
    _security = None
    def __init__(self, security):
        self._security = security

class Config(object):
    """Represents the operations that can be performed on the config store, properties and directories"""
    _system = None
    def __init__(self, system):
        self._system = system