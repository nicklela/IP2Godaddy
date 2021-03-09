import json
import logging
import os

class Configuration:
    DEFAULT_CONFIG = "config.json.default"

    def __init__(self, config = DEFAULT_CONFIG):
        self._file_path=config
        self._settings = {}

    def load(self):
        with open(self._file_path, 'r') as json_file:
            temp_settings = json.load(json_file)

            if 'domain' not in temp_settings:
                raise ValueError('domain property is required')

            if 'key' not in temp_settings:
                raise ValueError('key property is required')

            if 'secret' not in temp_settings:
                raise ValueError('secret property is required')

            self._settings = temp_settings

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
                self.load()
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

    def dump(self):
        logging.info('Configuration file: ' + self._file_path)
        logging.info('Configuration: ' + json.dumps(self._settings))
