import logging
import requests
import json
import os
from networking import HttpQuery
from ipaddress import ip_address, IPv4Address
  
class IPType:

    TYPE_IPV4 = 0
    TYPE_IPV6 = 1

class Provider:

    def __init__(self):
        self._domain = None
        self._name = None
        self._ip = None
        self._ipv6 = None
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
    def ipv6(self):
        return self._ipv6

    @ip.setter
    def ipv6(self, new_ip):
        self._ipv6 = new_ip

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    def __str__(self) -> str:
        return "domain: " + self.domain + " ip: " + self.ip + " ipv6: " + self.ipv6

    def isDomainExist(self, uri, header):
        data = self.query.get(uri, header)
        if (data is None or data.status_code != requests.codes.ok):
            return False
        logging.debug('Recv: {0} {1}'.format(data.status_code, data.text))
        return True

    def getRemoteIp(self, uri: str, header: str, type = IPType.TYPE_IPV4) -> True:

        if (type == IPType.TYPE_IPV4):
            ip = self._ip
        else:
            ip = self._ipv6

        if ip is not None:
            return ip

        """
        Get remote ip from DNS provider
        """
        data = self.query.get(uri, header)
        if (data is None or data.status_code != requests.codes.ok):
            return None

        logging.debug('Recv: {0} {1}'.format(data.status_code, data.text))
        record = json.loads(data.text)

        if len(record) == 0 or 'data' not in record[0]:
            return None

        ip = record[0]['data']
        if (type == IPType.TYPE_IPV4):
            self._ip = ip
        else:
            self._ipv6 = ip

        return ip

    def setRemoteIp(self, url: str, header: str, content: str, type = IPType.TYPE_IPV4) -> bool:
        data = self.query.put(url, header, content)        
        if (data is None or data.status_code != requests.codes.ok):
            return False

        logging.debug('Recv: {0} {1}'.format(data.status_code, data.text))
        """
        remote ip is updated
        """

        if (type == IPType.TYPE_IPV4):
            self._ip = None
        else:
            self._ipv6 = None

        return True

    def addRemoteIp(self, url: str, header: str, content: str, type = IPType.TYPE_IPV4) -> bool:
        data = self.query.patch(url, header, content)        
        if (data is None or data.status_code != requests.codes.ok):
            return False

        logging.debug('Recv: {0} {1}'.format(data.status_code, data.text))
        """
        remote ip is updated
        """
        if (type == IPType.TYPE_IPV4):
            self._ip = None
        else:
            self._ipv6 = None

        return True

    def getIPAddressType(self, IP: str) -> int:
        try:
            return IPType.TYPE_IPV4 if type(ip_address(IP)) is IPv4Address else IPType.TYPE_IPV6
        except ValueError:
            return None

class GoDaddy(Provider):

    def __init__(self, domain: str, name: str, key: str, secret: str):
        self._api = 'https://api.godaddy.com/v1/domains/'
        super(GoDaddy, self).__init__()
        self.domain = domain
        self.name = name
        self._key = key
        self._secret = secret
        self._header = {'accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'sso-key ' + self._key + ':' + self._secret}

    def isDomainExist(self):
        return super(GoDaddy, self).isDomainExist(self._api + self.domain, self._header)
        
    @property
    def ip(self):
        return super(GoDaddy, self).getRemoteIp(self._api + self.domain + '/records/A/' + self.name, self._header, IPType.TYPE_IPV4)

    @property
    def ipv6(self):
        return super(GoDaddy, self).getRemoteIp(self._api + self.domain + '/records/AAAA/' + self.name, self._header, IPType.TYPE_IPV6)

    @ip.setter
    def ip(self, new_ip):
        if super(GoDaddy, self).getIPAddressType(new_ip) != IPType.TYPE_IPV4:
            raise ValueError("IP " + new_ip + " is not IPv4 address")

        if self.ip is None:
            data = '[{"data": "' + new_ip + '", "name":"' + self.name + '","ttl":3600,"type":"A"}]'
            logging.debug('content: ' + data)
            super(GoDaddy, self).addRemoteIp(self._api + self.domain + '/records', self._header, data, IPType.TYPE_IPV4)
        else:
            data = '[{"data": "' + new_ip + '", "name":"' + self.name + '","ttl":3600,"type":"A"}]'
            logging.debug('content: ' + data)
            super(GoDaddy, self).setRemoteIp(self._api + self.domain + '/records/A/' + self.name, self._header, data, IPType.TYPE_IPV4)

    @ipv6.setter
    def ipv6(self, new_ip):
        if super(GoDaddy, self).getIPAddressType(new_ip) != IPType.TYPE_IPV6:
            raise ValueError("IP " + new_ip + " is not IPv6 address")

        if self.ipv6 is None:
            data = '[{"data": "' + new_ip + '", "name":"' + self.name + '","ttl":3600,"type":"AAAA"}]'
            logging.debug('content: ' + data)
            super(GoDaddy, self).addRemoteIp(self._api + self.domain + '/records', self._header, data, IPType.TYPE_IPV6)
        else:
            data = '[{"data": "' + new_ip + '", "name":"' + self.name + '","ttl":3600,"type":"AAAA"}]'
            logging.debug('content: ' + data)
            super(GoDaddy, self).setRemoteIp(self._api + self.domain + '/records/AAAA/' + self.name, self._header, data, IPType.TYPE_IPV6)

    def __str__(self) -> str:
        return "api: " + self._api + os.linesep + "header: " + self._header + os.linesep + super(GoDaddy, self).__str__()
