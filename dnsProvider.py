import logging
import requests
import json
from networking import HttpQuery

class Provider:

    def __init__(self):
        self._domain = None
        self._ip = None
        self._name = None
        self._remote_ip = None
        self.query = HttpQuery()

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, domain):
        self._domain = domain

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, new_ip):
        self._ip = new_ip

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    def dump(self):
        logging.debug('domain: ' + self.domain)
        logging.debug('ip: ' + self.ip)

    def isDomainExist(self, uri, header):
        data = self.query.get(uri, header)
        if (data.status_code != requests.codes.ok):
            return False
        logging.debug('Recv: {0} {1}'.format(data.status_code, data.text))
        return True

    def getRemoteIp(self, uri, header):

        if self._remote_ip is not None:
            return self._remote_ip

        data = self.query.get(uri, header)
        logging.debug('Recv: {0} {1}'.format(data.status_code, data.text))
        if (data.status_code != requests.codes.ok):
            return None

        record = json.loads(data.text)

        if len(record) == 0 or 'data' not in record[0]:
            return None

        self._remote_ip = record[0]['data']
        return self._remote_ip

    def setRemoteIp(self, url, header, content):
        data = self.query.put(url, header, content)        
        if (data.status_code != requests.codes.ok):
            return False
        logging.debug('Recv: {0} {1}'.format(data.status_code, data.text))
        """
        remote ip is updated
        """
        self._remote_ip = None
        return True

    def addRemoteIp(self, url, header, content):
        data = self.query.patch(url, header, content)        
        if (data.status_code != requests.codes.ok):
            return False
        logging.debug('Recv: {0} {1}'.format(data.status_code, data.text))
        return True


class GoDaddy(Provider):

    def __init__(self, domain, name, ip, key, secret):
        self._api = 'https://api.godaddy.com/v1/domains/'
        super(GoDaddy, self).__init__()
        self.domain = domain
        self.ip = ip
        self.name = name
        self._key = key
        self._secret = secret
        self._header = {'accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'sso-key ' + self._key + ':' + self._secret}

    def isDomainExist(self):
        return super(GoDaddy, self).isDomainExist(self._api + self.domain, self._header)
        
    @property
    def remote_ip(self):
        return super(GoDaddy, self).getRemoteIp(self._api + self.domain + '/records/A/' + self.name, self._header)

    @remote_ip.setter
    def remote_ip(self, new_ip):
        if self.remote_ip is None:
            data = '[{"data": "' + new_ip + '", "name":"' + self.name + '","ttl":3600,"type":"A"}]'
            logging.debug('content: ' + data)
            super(GoDaddy, self).addRemoteIp(self._api + self.domain + '/records', self._header, data)
        else:
            data = '[{"data": "' + new_ip + '", "name":"' + self.name + '","ttl":3600,"type":"A"}]'
            logging.debug('content: ' + data)
            super(GoDaddy, self).setRemoteIp(self._api + self.domain + '/records/A/@', self._header, data)

    def dump(self):
        super(GoDaddy, self).dump()
        logging.debug('api: ' + self._api)
        logging.debug('header: ' + self.header)
