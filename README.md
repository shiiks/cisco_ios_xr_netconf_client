# cisco_ios_xr_netconf_client
This script uses the ncclient Python library to interact with the always-on Cisco DevNet sandbox to manage Ethernet VLANs on a Cisco IOS-XR switch.

## Prerequisites
To use this script, you will need:

A Cisco DevNet account (you can sign up for free at https://developer.cisco.com/)
Access to the always-on IOS-XR sandbox (you can find more information on how to access it at https://developer.cisco.com/docs/ios-xr/#!getting-access-to-the-ios-xr-sandbox/getting-access-to-the-ios-xr-sandbox)

## Installation
To install the required libraries, run:

```
pip install ncclient
```

## Usage
To use the script, simply run:

```
python ios_xr_netconf_client.py
```

The script uses .env to store following information:

The IP address of the IOS-XR switch
Your Cisco DevNet sandbox username
Your Cisco DevNet sandbox password
Once you have provided this information by creating a .env file, the script will use NETCONF to connect to the IOS-XR switch and fetch the current VLAN configuration.

## .env file format
```
HOST=<IP_ADDRESS>
PORT=<PORT>
USERNAME_IOS_XR=<USERNAME>
PASSWORD=<PASSWORD>
HOSTKEY_VERIFY=False
ALLOW_AGENT=False
LOOK_FOR_KEYS=False
FILTER_FILE=filters.xml
```

## Parameters
The script takes 2 parameters to perform the following options:

View VLANs -  provide `--view` as a parameter
Add VLAN -  provide `--edit` as a parameter
If you provide option `--view`, the script will display the current VLAN configuration by using a filter mentioned in filters.xml.
If you provide option `--edit`, the script will add the VLAN to the switch using the state.yml file configuration. If it does nothing then try changing some values in the state.yml file

## License
This script is licensed under the BSD 3-Clause License. See the LICENSE file for more information.