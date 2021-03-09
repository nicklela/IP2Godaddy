import argparse
import logging
from config import Configuration
from dnsProvider import GoDaddy
from networking import NetInterface

"""
Debug log setting
"""
def debug_enabled():
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

def error_enabled():
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.ERROR, format=FORMAT)

def info_enabled():
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)

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
    Find interface IP address
    """
    interface = NetInterface(config.interface)
    ipaddr = interface.ip
    logging.debug('IP address of ' + config.interface + ' is: ' + ipaddr)

    """
    Upate DNS
    """
    logging.debug('Update ' + ipaddr + ' for domain: {0}'.format(config.domain))
    dnsProvider = GoDaddy(config.domain, config.name, ipaddr, config.key, config.secret)
    if dnsProvider.isDomainExist():
        remote_ip = dnsProvider.remote_ip
        if remote_ip is None:
            logging.error(config.name + '.' + config.domain + ' does not exist, will reate one')
            dnsProvider.remote_ip = ipaddr
            if dnsProvider.remote_ip == ipaddr:
                logging.info('Add ' + config.name + '.' + config.domain + ' with ' + ipaddr + ' successfully')
            else:
                logging.error('Add ' + config.name + '.' + config.domain + ' with ' + ipaddr + ' failed')
        elif remote_ip == ipaddr:
            logging.info('Remote ip is up to date: ' + ipaddr)
        else:
            logging.debug('Update ' + config.domain + ' from ' + remote_ip + ' to ' + ipaddr)
            dnsProvider.remote_ip = ipaddr
            if dnsProvider.remote_ip == ipaddr:
                logging.info('Update ' + config.domain + ' from ' + remote_ip + ' to ' + ipaddr + ' successfully')
            else:
                logging.error('Update ' + config.domain + ' from ' + remote_ip + ' to ' + ipaddr + ' failed')
    else:
        logging.error(config.domain + ' does not exist')

if __name__ == "__main__":

    #debug_enabled()
    info_enabled()
    main()

