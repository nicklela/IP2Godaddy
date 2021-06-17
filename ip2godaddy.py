import argparse
import logging
import os
from config import Configuration
from dnsProvider import GoDaddy, IPType
from networking import NetInterface

"""
Debug log setting
"""
LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
def debug_enabled():
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

def info_enabled():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

def updateIP(provider: GoDaddy, ipaddr: str, type = IPType.TYPE_IPV4) -> bool:

    if type == IPType.TYPE_IPV4:
        provider.ip = ipaddr
        if provider.ip == ipaddr:
            return True
    else:
        provider.ipv6 = ipaddr
        if provider.ipv6 == ipaddr:
            return True

    return False

def updateDNS(ipaddr: str, ipaddrv6: str, config: Configuration):
    logging.debug('Update ' + ipaddr + ' for domain: {0}'.format(config.domain))
    if ipaddrv6 != None:
        logging.debug('Update ' + ipaddrv6 + ' for domain: {0}'.format(config.domain))

    dnsProvider = GoDaddy(config.domain, config.name, config.key, config.secret)
    if dnsProvider.isDomainExist():

        remote_ip = dnsProvider.ip
        if remote_ip is None:
            logging.error('Type A record for ' + config.fulldomain + ' does not exist, will reate one')
            if updateIP(dnsProvider, ipaddr, IPType.TYPE_IPV4) == True:
                logging.info('[' + config.fulldomain + '] add ' + ipaddr + ' successfully')
            else:
                logging.error('[' + config.fulldomain + '] add ' + ipaddr + ' failed')
        elif remote_ip == ipaddr:
            logging.info('[' + config.fulldomain + '] remote ip is up to date: ' + ipaddr)
        else:
            logging.debug('[' + config.fulldomain + '] update from ' + remote_ip + ' to ' + ipaddr)
            if updateIP(dnsProvider, ipaddr, IPType.TYPE_IPV4) == True:
                logging.info('[' + config.fulldomain + '] update from ' + remote_ip + ' to ' + ipaddr + ' successfully')
            else:
                logging.error('[' + config.fulldomain + '] update from ' + remote_ip + ' to ' + ipaddr + ' failed')

        if ipaddrv6 == None:
            return

        remote_ip = dnsProvider.ipv6
        if remote_ip is None:
            logging.error('Type AAA record for ' + config.fulldomain + ' does not exist, will reate one')
            if updateIP(dnsProvider, ipaddrv6, IPType.TYPE_IPV6) == True:
                logging.info('[' + config.fulldomain + '] add ' + ipaddrv6 + ' successfully')
            else:
                logging.error('[' + config.fulldomain + '] add ' + ipaddrv6 + ' failed')
        elif remote_ip == ipaddrv6:
            logging.info('[' + config.fulldomain + '] remote ipv6 is up to date: ' + ipaddrv6)
        else:
            logging.debug('[' + config.fulldomain + '] update from ' + remote_ip + ' to ' + ipaddrv6)
            if updateIP(dnsProvider, ipaddrv6, IPType.TYPE_IPV6) == True:
                logging.info('[' + config.fulldomain + '] update from ' + remote_ip + ' to ' + ipaddrv6 + ' successfully')
            else:
                logging.error('[' + config.fulldomain + '] update from ' + remote_ip + ' to ' + ipaddrv6 + ' failed')                
    else:
        logging.error(config.domain + ' does not exist')

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
    if config.ipv6 == True:
        ipaddrv6 = interface.ipv6
    else:
        ipaddrv6 = None

    logging.debug('IP address of ' + config.interface + ' is: ' + ipaddr)
    if ipaddrv6 != None:
        logging.debug('IPv6 address of ' + config.interface + ' is: ' + ipaddrv6)

    """
    public ip check
    """
    public_ip = interface.public_ip
    if public_ip is not None and ipaddr != public_ip:
        logging.warning('interface ip: ' + ipaddr + ' is different from public ip: ' + public_ip + ', you may be behind NAT router')

    """
    Upate DNS
    """
    try:
        updateDNS(ipaddr, ipaddrv6, config)
    except Exception as e:
        logging.error('Failed to update ' + ipaddr + ' for ' + config.fulldomain + ' due to {0}'.format(e))
        raise RuntimeError('Failed to update ' + ipaddr + ' for ' + config.fulldomain)  from e

if __name__ == "__main__":

    #debug_enabled()
    info_enabled()
    main()

