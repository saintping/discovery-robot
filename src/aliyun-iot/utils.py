# -*- coding: utf-8 -*-
# Author: matthewliu
# Created: 2019/6/30
#

import hmac
import socket
import struct
from hashlib import sha1

import fcntl


def hmacsha1(key, text):
    hmac_code = hmac.new(key.encode(encoding="utf-8"), text.encode(encoding="utf-8"), sha1)
    return hmac_code.hexdigest()


def get_ip(ifname):
    """
    :param ifname: eth0 and so
    :return:
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        ip = socket.inet_ntoa(fcntl.ioctl(sock.fileno(),
                                          0x8915,  # SIOCGIFADDR
                                          struct.pack('256s', bytes(ifname[:15], 'utf-8')))[20:24])
        sock.close()
        return ip
    except:
        return "0.0.0.0"
