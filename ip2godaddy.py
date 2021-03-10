import argparse
import logging
import os
from config import Configuration
from dnsProvider import GoDaddy
from networking import NetInterface

"""
Debug log setting
"""
LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
def debug_enabled():
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

def info_enabled():
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

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

    logging.info(os.path.basename(__file__) + ' start')
    
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
    Check to see if we need log file
    """
    if config.log is not None:
        fileLog = logging.FileHandler(config.log)
        logFormat = logging.Formatter(LOG_FORMAT)
        fileLog.setFormatter(logFormat)
        rootLog = logging.getLogger()
        rootLog.addHandler(fileLog)
        logging.debug('Log file: ' + config.log)

    """
    Find interface IP address
    """
    try:
        interface = NetInterface(config.interface)
    except Exception as e:
        logging.error('Fail to locate interface: ' + config.interface + ' due to {0}'.format(e))
        raise RuntimeError('Fail to locate interface') from e
        
    ipaddr = interface.ip
    logging.debug('IP address of ' + config.interface + ' is: ' + ipaddr)

    """
    public ip check
    """
    public_ip = interface.public_ip
    if public_ip is not None and ipaddr != public_ip:
        logging.warn('interface ip: ' + ipaddr + ' is different from public ip: ' + public_ip + ', you may be behind NAT router')

    """
    Upate DNS
    """
    logging.debug('Update ' + ipaddr + ' for domain: {0}'.format(config.domain))
    dnsProvider = GoDaddy(config.domain, config.name, ipaddr, config.key, config.secret)
    if dnsProvider.isDomainExist():
        remote_ip = dnsProvider.remote_ip
        if remote_ip is None:
            logging.error(config.fulldomain + ' does not exist, will reate one')
            dnsProvider.remote_ip = ipaddr
            if dnsProvider.remote_ip == ipaddr:
                logging.info('[' + config.fulldomain + '] add ' + ipaddr + ' successfully')
            else:
                logging.error('[' + config.fulldomain + '] add ' + ipaddr + ' failed')
        elif remote_ip == ipaddr:
            logging.info('[' + config.fulldomain + '] remote ip is up to date: ' + ipaddr)
        else:
            logging.debug('[' + config.fulldomain + '] update from ' + remote_ip + ' to ' + ipaddr)
            dnsProvider.remote_ip = ipaddr
            if dnsProvider.remote_ip == ipaddr:
                logging.info('[' + config.fulldomain + '] update from ' + remote_ip + ' to ' + ipaddr + ' successfully')
            else:
                logging.error('[' + config.fulldomain + '] update from ' + remote_ip + ' to ' + ipaddr + ' failed')
    else:
        logging.error(config.domain + ' does not exist')

if __name__ == "__main__":

    #debug_enabled()
    info_enabled()
    main()

