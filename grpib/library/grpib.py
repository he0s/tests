#!/usr/bin/env python

import fcntl
import psutil
import os
import socket
import struct

from ansible.module_utils.basic import AnsibleModule


def getFlags(path, iface):
    """
    Function to get flags of a network interface.

    Args:
        path - string, a path, where information about an interface
        can be found;
        iface - string, name of an interface to get data.

    Returns:
        Dict with information if an interface is in PROMISC mode
        and it's status.
    """

    nulls = '\0'*256

    SIOCGIFFLAGS = 0x8913

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # copied from https://www.safaribooksonline.com/library/view/python-cookbook/0596001673/ch07s05.html # noqa
    result = fcntl.ioctl(s.fileno(), SIOCGIFFLAGS, iface + nulls)
    flags, = struct.unpack('h', result[16:18])

    if_stat_bit = int("{0:b}".format(flags)) & (1 << 0)
    promisc_bit = int("{0:b}".format(flags)) & (1 << 8)

    if promisc_bit:
        return {'promisc': 1, 'iface_stat': if_stat_bit}
    else:
        return {'promisc': 0, 'iface_stat': if_stat_bit}


def getNetIfaceList(path):
    """
    Function to get list of interfaces.

    Args:
        path - string, path to the system's directory, where script can
        gather list of network interfaces.

    Returns:
        List of interfaces if script find it,
        Fasle - otherwise.
    """
    except_list = ["bonding_masters"]

    if os.path.exists(path):
        iface_list = [i for i in os.listdir(path) if i not in except_list]
        return iface_list

    else:
        return False


def main():
    module = AnsibleModule(argument_spec={})

    path = '/sys/class/net/'

    result = {}
    result.update({'mem': psutil.virtual_memory().total})

    data = getNetIfaceList(path)
    if data:
        ifaces = {iface: getFlags(path, iface) for iface in data}

    count = 0
    for key in ifaces:
        if ifaces[key]['promisc']:
            count += 1

    result.update({'promisc': count})

    if 'tun0' in ifaces.keys():
        result.update({'vpn': 1})
    else:
        result.update({'vpn': 0})

    module.exit_json(changed=False, meta=result)


if __name__ == "__main__":
    main()
