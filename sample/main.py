#!/usr/bin/env python3

from model import Profile, OpenVpn, Pool
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(message)s")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="script that helps with otp-code entering routine")
    parser.add_argument("mode", choices=["ls", "on", "off"])
    parser.add_argument("config", choices=Pool.get_profile_names(), nargs="?", default="example")
    args = parser.parse_args()

    profile = Profile(args.config)
    OpenVpn.do(args.mode, profile)
