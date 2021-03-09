import argparse
import logging
from config import Configuration
from dnsProvider import GoDaddy

"""
Debug log setting
"""
def debug_enabled():
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

"""
Main function
"""
def main():
    """
    parse user input
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="specify the config.json in other place", default=Configuration.DEFAULT_CONFIG)
    args = parser.parse_args()

    """
    Get config
    """
    config = Configuration(args.config)
    try:
        config.load()
    except Exception as e:
        logging.error('Fail to load configuration from ' + config.file + ' due to {0}'.format(e))
        raise RuntimeError('Fail to load configuration') from e

    logging.debug('config {0}'.format(config.settings))

    """
    Upate DNS
    """
    logging.info('Update IP for domain: {0}'.format(config.domain))
    dnsProvider = GoDaddy(config.domain)
    dnsProvider.dump()

if __name__ == "__main__":

    debug_enabled()
    main()

