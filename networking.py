import netifaces
import logging
import requests
import json
import time

RETRY_COUNT=3
TIMEOUT=5
SLEEP=5

class HttpQuery:

    def __init__(self):
        self._timeout = TIMEOUT
        self._retry = RETRY_COUNT

    def retry(sleep, retry = RETRY_COUNT):
        def decorator(func):
            def wrapper(*args, **kwargs):
                retries = 0
                while retries < retry:
                    try:
                        result = func(*args, **kwargs)
                    except requests.exceptions.Timeout:
                        retries += 1
                        logging.error('timed out while access: ' + args[1] + ', retry {0}/{1} in {2} seconds...'.format(retries, retry, sleep))
                        time.sleep(sleep)
                    else:
                        return result
                return None
            return wrapper
        return decorator


    def post(self, url, json_data):
        try:
            result = requests.post(url, json = json_data, timeout = self._timeout)
        except requests.exceptions.Timeout:
            logging.error('Timed out while doing post: ' + url)
        except Exception as e:
            logging.exception('Exception while doing post')
        else:
            return result
        return None

    @retry(SLEEP, RETRY_COUNT)
    def get(self, url, header):
        return requests.get(url, headers = header, timeout = self._timeout)

    def put(self, url, header, data):
        try:
            result = requests.put(url, headers = header, data = data, timeout = self._timeout)
        except requests.exceptions.Timeout:
            logging.error('Timed out while doing put: ' + url)
        except Exception as e:
            logging.exception('Exception while doing put')
        else:
            return result
        return None

    def patch(self, url, header, data):
        try:
            result = requests.patch(url, headers = header, data = data, timeout = self._timeout)
        except requests.exceptions.Timeout:
            logging.error('Timed out while doing patch' + url)
        except Exception as e:
            logging.exception('Exception while doing patch')
        else:
            return result
        return None

class NetInterface:

    def __init__(self, ifName = 'eth0'):
        self.interface = ifName
        self.public_ip_api = 'https://ipinfo.io/json'
        self.query = HttpQuery()

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
    def public_ip(self):
        data = self.query.get(self.public_ip_api, None)
        if (data is None or data.status_code != requests.codes.ok):
            return None
        json_data = json.loads(data.text)
        if 'ip' not in json_data:
            return None

        return json_data['ip']

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
        
