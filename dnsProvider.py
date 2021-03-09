import logging
from networking import HttpQuery

class Provider:

    def __init__(self, domain):
        self._domain = domain

    @property
    def domain(self):
        return self._domain

class GoDaddy(Provider):

    def __init__(self, domain):
        self._api = 'https://api.godaddy.com/v1/domains/'
        super(GoDaddy, self).__init__(domain)


    def dump(self):
        logging.debug('domain: ' + self._domain)
        logging.debug('api: ' + self._api)
