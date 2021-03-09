import json
import logging
import os

class Configuration:
    DEFAULT_CONFIG = "config.json.default"
    file_path = ""
    settings = {}

    def __init__(self, config = DEFAULT_CONFIG):
        self.file_path=config

    def load(self):
        with open(self.file_path, 'r') as json_file:
            self.settings = json.load(json_file)

    def dump(self):
        logging.info('Configuration file: ' + self.file_path)
        logging.info('Configuration: ' + json.dumps(self.settings))
