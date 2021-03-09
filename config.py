import json
import logging
import os

class Configuration:
    DEFAULT_CONFIG = "config.json.default"

    def __init__(self, config = DEFAULT_CONFIG):
        self._file_path = config
        self._settings = {}

    def __isValid(self, setting):
        if 'domain' not in setting or not setting['domain']:
            return False
            
        if 'key' not in setting or not setting['key']:
            return False

        if 'secret' not in setting or not setting['secret']:
            return False

        if 'interface' not in setting or not setting['interface']:
            return False

        if 'name' not in setting or not setting['name']:
            return False

        return True        

    def __load(self, path):
        with open(path, 'r') as json_file:
            temp_settings = json.load(json_file)

            if self.__isValid(temp_settings) == False:
                raise ValueError('Invalid configuration file')

            self._settings = temp_settings

    def load(self):
        return self.__load(self._file_path)

    @property
    def settings(self):
        return self._settings

    @property
    def file(self):
        return self._file_path

    @file.setter
    def file(self, new_file):
        if os.path.isfile(new_file):
            try:
                self.__load(new_file)
            except Exception as e:
                raise Exception from e

            self._file_path = new_file
            logging.info('configuraiton is updated from {0}'.format(self._file_path))
        else:
            raise FileNotFoundError('file: ' + new_file + ' is not found')

    @property
    def domain(self):
        return self._settings['domain']

    @property
    def key(self):
        return self._settings['key']

    @property
    def secret(self):
        return self._settings['secret']

    @property
    def interface(self):
        return self._settings['interface']

    @property
    def name(self):
        return self._settings['name']

    def dump(self):
        logging.info('Configuration file: ' + self._file_path)
        logging.info('Configuration: ' + json.dumps(self._settings))
