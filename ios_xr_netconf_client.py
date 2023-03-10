#!/usr/bin/env python

"""Author: Shikhar Saran Srivastava 
Purpose: Using NETCONF with ncclient to collect interfaces
configs on a Cisco IOS-XR switch via the always-on Cisco DevNet sandbox.
"""

import logging
import json
import socket
import os
from dotenv import load_dotenv
from cachetools import cached, TTLCache
from ncclient import manager, transport
import xmltodict

load_dotenv()
logging.basicConfig(filename='app.log', level=logging.DEBUG, filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

class IOSXR:
    def __init__(self):
        with open(os.getenv('FILTER_FILE'), 'r') as filter:
            self.filters = str(filter.read())
        
    def get_configs(self, params):
        """
        This function fetches the list of interfaces filtering out subset all interfaces from the IOS XR devices.
        :param: params: The parameters needed to make connection to the IOS XR router device.
        :return: List of interfaces if found else returns empty list.
        """
        try:
            interfaces = []
            with manager.connect(**params) as connection:
                context = connection.get_config(source='running', filter=('subtree', self.filters)).data_xml
                with open("%s_1.xml" % params['host'], 'w') as file:
                    file.write(context)
                interfaces = xmltodict.parse(context)
                interfaces = interfaces['data']['interfaces']['interface']
                logging.info("List of Interfaces found...")
                for interface in interfaces:
                    logging.info(f"Name of the Interface: {interface['interface-name']}")
                    logging.info(f"Description: {interface['description']}")
                    logging.info(f"IPV4 Address: {interface['ipv4']['addresses']['address']['address']}")
                    logging.info(f"IPV4 Netmask: {interface['ipv4']['addresses']['address']['netmask']}")
        except transport.errors.AuthenticationError as exception:
            interfaces = {
                "ERROR": f"Authentication failed, please check the username and password and try again."
            }        
        except json.decoder.JSONDecodeError as exception:
            interfaces = {
                "ERROR": f"JSONDecodeError occured while communicating to {url} because {exception}"
            }
        except socket.gaierror as exception:
            interfaces = {
                "ERROR": f"Socket error occured while communciation to the IOS XR host URL, please check the URL and try again."
            }
        logging.info(interfaces)
        return interfaces
    
    def edit_configs(self, params):
        """
        This function edits the list of interfaces by reading a subset from a yaml file for the IOS XR devices.
        :param: params: The parameters needed to make connection to the IOS XR router device.
        :return: List of interfaces if found else returns empty list.
        """
        try:
            with manager.connect(**params) as connection:
                response = update_interfaces(connection, 'state.yml')
        except transport.errors.AuthenticationError as exception:
            interfaces = {
                "ERROR": f"Authentication failed, please check the username and password and try again."
            }        
        except json.decoder.JSONDecodeError as exception:
            interfaces = {
                "ERROR": f"JSONDecodeError occured while communicating to {url} because {exception}"
            }
        except socket.gaierror as exception:
            interfaces = {
                "ERROR": f"Socket error occured while communciation to the IOS XR host URL, please check the URL and try again."
            }
        logging.info(interfaces)
        return interfaces
            
            
if __name__ == "__main__":
    ios_xr_client = IOSXR()
    params = {
        'host': os.getenv('HOST'),
        'port': int(os.getenv('PORT')),
        'username': os.getenv('USERNAME_IOS_XR'),
        'password': os.getenv('PASSWORD'),
        'hostkey_verify': False if os.getenv('HOSTKEY_VERIFY') == 'False' else True,
        "allow_agent": False if os.getenv('ALLOW_AGENT') == 'False' else True,
        "look_for_keys": False if os.getenv('LOOK_FOR_KEYS') == 'False' else True
    }
    ios_xr_client.get_configs(params)