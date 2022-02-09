#!/usr/bin/env python3

import sys, logging
from model import Profile, Credentials
from vpn import OpenVpn

logging.basicConfig(level=logging.INFO)


def checkArgs(args):
        if len(args) == 2 and args[1] == 'list':
            return None, args[1]
        if len(args) < 3:
            raise ValueError('Insufficient arguments! You must specify \"ini\"-filename and mode (on/off/list)')
        elif not Profile(args[1]).exists():
            raise ValueError(f'Such configuration not found > {args[1]}.ini')
        elif args[2] not in ['on', 'off', 'list']:
            raise ValueError('You must specify execution mode (on/off/list)')
        else: return args[1], args[2]


if __name__ == '__main__':
    profilename, mode = checkArgs(sys.argv)
    if mode == 'list':
        OpenVpn.printSessions()
    else:
        creds = Credentials(profilename)
        vpn = OpenVpn(creds)
        if mode == "off": vpn.stopAll()
        elif mode == "on": vpn.start()