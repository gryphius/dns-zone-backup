#!/usr/bin/python
from dnsbackup.core import DNSBackup
import logging
import sys
import os

if __name__== '__main__':
    if len(sys.argv)<2:
        print "Usage: dns-zone-backup.py /path/to/configfile"
        sys.exit(1)
    config = sys.argv[1]
    if not os.path.exists(config):
        print "Config %s not found"%config
        sys.exit(1)
    logging.basicConfig(level=logging.DEBUG)
    backup = DNSBackup()
    backup.config.readfp(open(config,'r'))
    backup.run()
