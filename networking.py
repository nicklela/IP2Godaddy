import netifaces
import logging
import requests

class HttpQuery:

    def __init__(self):
        self._timeout = 2

    def post(self, url, json_data):
        result = requests.post(url, json = json_data, timeout = self._timeout)
        return result

    def get(self, url, header):
        return requests.get(url, headers = header, timeout = self._timeout)

    def put(self, url, header, data):
        return requests.put(url, headers = header, data = data, timeout = self._timeout)

    def patch(self, url, header, data):
        return requests.patch(url, headers = header, data = data, timeout = self._timeout)

class NetInterface:

    def __init__(self, ifName = 'eth0'):
        self.interface = ifName

    def __isValidInterface(self, interface):
        interfaces = netifaces.interfaces()
        logging.debug('available interfaces: {0}'.format(interfaces))
        if interface not in netifaces.interfaces():
            return False

        return True

    @property
    def ip(self):
        ip_address = netifaces.ifaddresses(self.interface)[netifaces.AF_INET][0]['addr']
        logging.debug(self.interface + ' ip: {0}'.format(ip_address))
        return ip_address

    @property
    def interface(self):
        return self._interface

    @interface.setter
    def interface(self, new_interface):
        #
        # verify interface
        #
        if self.__isValidInterface(new_interface):
            self._interface = new_interface
        else:
            raise ValueError('Invalid interface: {0}'.format(new_interface))
        
