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
from ncclient.operations import RaiseMode
import xmltodict
import yaml
import gettext


load_dotenv()
logging.basicConfig(filename='app.log', level=logging.DEBUG, filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

class IOSXR:
    def __init__(self):
        self.translations = gettext.translation('messages', localedir="locales", languages=[os.getenv('LANGUAGE')])
        self.translations.install()
        self._ = self.translations.gettext
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
                logging.info(connection)
                context = connection.get_config(source='running', filter=('subtree', self.filters)).data_xml
                with open("%s_1.xml" % params['host'], 'w') as file:
                    file.write(context)
                interfaces = xmltodict.parse(context)
                interfaces = interfaces['data']['interfaces']['interface']
                logging.info(self._('list_of_interfaces'))
                for interface in interfaces:
                    logging.info(f"{self._('name_of_interface')}{interface['interface-name']}")
                    logging.info(f"{self._('description')}{interface['description']}")
                    logging.info(f"{self._('IPV4_address')}{interface['ipv4']['addresses']['address']['address']}")
                    logging.info(f"{self._('IPV4_netmask')}{interface['ipv4']['addresses']['address']['netmask']}")
        except transport.errors.AuthenticationError as exception:
            interfaces = {
                "ERROR": self._('AuthenticationError')
            }        
        except json.decoder.JSONDecodeError as exception:
            interfaces = {
                "ERROR": self._('JSONDecodeError').format(host=params['host'], exception=exception)
            }
        except transport.errors.SSHError as exception:
            interfaces = {
                "ERROR": self._('SSHError').format(host=params['host'], exception=exception)
            }
        except socket.gaierror as exception:
            interfaces = {
                "ERROR": self._('gaierror').format(host=params['host'], exception=exception)
            }
        logging.info(interfaces)
        return interfaces
    
    
    def update_interfaces(self, connection, config_file):
        interfaces_to_update = []
        try:
            with open(config_file, 'r') as state_file:
                configuration_state = yaml.safe_load(state_file)
                for description, ipv4 in configuration_state["interfaces"].items():
                    interfaces_to_update.append({
                        "description": description,
                        "ipv4": {
                            "addresses": {
                                "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XR-um-if-ip-address-cfg", 
                                "address": {
                                    "address": ipv4['addresses']['address']['address'], 
                                    "netmask": ipv4['addresses']['address']['netmask'],
                                    },
                                },
                        },
                    })
                
            configuration_parent = {
                "config": {
                    "interfaces": {
                        "@xmlns": "http://cisco.com/ns/yang/Cisco-IOS-XR-um-if-ip-address-cfg",
                        "interface": interfaces_to_update
                    }
                }
            }
                
            xml_payload = xmltodict.unparse(configuration_parent)
            with connection.locked(target="candidate"):
                connection.raise_mode = RaiseMode.NONE
                response = connection.edit_config(target="candidate", config=xml_payload)
                validate = connection.validate(source="candidate")
                connection.raise_mode = RaiseMode.ALL
                
                if response.ok and validate.ok:
                    connection.commit()
                else:
                    connection.discard()
        except json.decoder.JSONDecodeError as exception:
            interfaces_error = {
                "ERROR": self._('JSONDecodeError').format(host=params['host'], exception=exception)
            }
            logging.error(interfaces_error)
        return interfaces_to_update
    
    
    def edit_configs(self, params):
        """
        This function edits the list of interfaces by reading a subset from a yaml file for the IOS XR devices.
        :param: params: The parameters needed to make connection to the IOS XR router device.
        :return: List of interfaces if found else returns empty list.
        """
        try:
            with manager.connect(**params) as connection:
                logging.info(connection)
                response = self.update_interfaces(connection, 'state.yml')
        except transport.errors.AuthenticationError as exception:
            interfaces = {
                "ERROR": self._('AuthenticationError')
            }        
        except json.decoder.JSONDecodeError as exception:
            interfaces = {
                "ERROR": self._('JSONDecodeError').format(host=params['host'], exception=exception)
            }
        except transport.errors.SSHError as exception:
            interfaces = {
                "ERROR": self._('SSHError').format(host=params['host'], exception=exception)
            }
        except socket.gaierror as exception:
            interfaces = {
                "ERROR": self._('gaierror').format(host=params['host'], exception=exception)
            }
        logging.info(interfaces)
        return interfaces
    
    
if __name__ == "__main__":
    ios_xr_client = IOSXR()
    params = {
        "host": os.getenv('HOST'),
        "port": int(os.getenv('PORT')),
        "username": os.getenv('USERNAME_IOS_XR'),
        "password": os.getenv('PASSWORD'),
        "hostkey_verify": False if os.getenv('HOSTKEY_VERIFY') == 'False' else True,
        "allow_agent": False if os.getenv('ALLOW_AGENT') == 'False' else True,
        "look_for_keys": False if os.getenv('LOOK_FOR_KEYS') == 'False' else True,
        "device_params": {"name": "iosxr"},
        "manager_params": {"timeout": 6330}
    }
    ios_xr_client.get_configs(params)
    ios_xr_client.edit_configs(params)