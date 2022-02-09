import netifaces
import logging
import requests
import json
import time
import os

RETRY_COUNT=3
TIMEOUT=5
SLEEP=5

class HttpQuery:

    def __init__(self):
        self._timeout = TIMEOUT
        self._retry = RETRY_COUNT

        http_proxy = os.getenv('http_proxy')
        https_proxy = os.getenv('https_proxy')
        if http_proxy is None and https_proxy is None:
            self._proxies = None
            logging.debug('No proxy settings found')
        else:
            self._proxies = { "http": http_proxy, "https": https_proxy }

    def retry(sleep, retry: int = RETRY_COUNT):
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


    def post(self, url: str, json_data: str):
        try:
            result = requests.post(url, json = json_data, timeout = self._timeout, proxies = self._proxies)
        except requests.exceptions.Timeout:
            logging.error('Timed out while doing post: ' + url)
        except Exception as e:
            logging.exception('Exception while doing post')
        else:
            return result
        return None

    @retry(SLEEP, RETRY_COUNT)
    def get(self, url: str, header: str):
        return requests.get(url, headers = header, timeout = self._timeout, proxies = self._proxies)

    def put(self, url: str, header: str, data):
        try:
            result = requests.put(url, headers = header, data = data, timeout = self._timeout, proxies = self._proxies)
        except requests.exceptions.Timeout:
            logging.error('Timed out while doing put: ' + url)
        except Exception as e:
            logging.exception('Exception while doing put')
        else:
            return result
        return None

    def patch(self, url: str, header: str, data):
        try:
            result = requests.patch(url, headers = header, data = data, timeout = self._timeout, proxies = self._proxies)
        except requests.exceptions.Timeout:
            logging.error('Timed out while doing patch' + url)
        except Exception as e:
            logging.exception('Exception while doing patch')
        else:
            return result
        return None

class NetInterface:

    def __init__(self, ifName: str = 'eth0'):
        self.interface = ifName
        self.public_ip_api = 'https://ipinfo.io/json'
        self.query = HttpQuery()

    def __isValidInterface(self, interface: str) -> bool:
        interfaces = netifaces.interfaces()
        logging.debug('available interfaces: {0}'.format(interfaces))
        if interface not in netifaces.interfaces():
            return False

        return True

    @property
    def ip(self) -> str:
        ip_address = netifaces.ifaddresses(self.interface)[netifaces.AF_INET][0]['addr']
        logging.debug(self.interface + ' ip: {0}'.format(ip_address))
        return ip_address

    @property
    def ipv6(self) -> str:
        try:
            ip_address = netifaces.ifaddresses(self.interface)[netifaces.AF_INET6][0]['addr']
        except KeyError as e:
            return None
            
        logging.debug(self.interface + ' ipv6: {0}'.format(ip_address))
        return ip_address

    @property
    def public_ip(self) -> str:
        data = self.query.get(self.public_ip_api, None)
        if (data is None or data.status_code != requests.codes.ok):
            return None
        json_data = json.loads(data.text)
        if 'ip' not in json_data:
            return None

        return json_data['ip']

    @property
    def interface(self) -> str:
        return self._interface

    @interface.setter
    def interface(self, new_interface: str):
        #
        # verify interface
        #
        if self.__isValidInterface(new_interface):
            self._interface = new_interface
        else:
            raise ValueError('Invalid interface: {0}'.format(new_interface))
        
