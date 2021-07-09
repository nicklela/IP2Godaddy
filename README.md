# IP2Godaddy
The tool to report your local IP address to Godaddy

# Configuration
* Copy default configuration file: *config.json.default* to your private folder. For example: ```cp config.json.default my_domain.json```
* Edit this file to add your settings. 
  ```
  {
  "domain": "your_domain",
  "name": "@",
  "key": "your_key",
  "secret": "your_secret",
  "interface": "eth0",
  "ipv6": "true",
  "log": "ip2godaddy.log"
  }
  ```
  * For the key and secret, please refer to GoDaddy API document: https://developer.godaddy.com/
  * "log" is optional.
  * Please have proper permission setting to this file and make sure that the key and secret will not be exposed to other people.

# Run
* use *-c* or *--config* to specify your configuration file. For example: ```python3 ip2godaddy.py -c /path/to/your/config.json```
