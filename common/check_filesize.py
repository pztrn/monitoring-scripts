#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Filesize checker for Icinga/Nagios.
# Checks for file size.
# Part of pztrn's Icinga additions.
# Copyright (c) 2013 - 2014, Stanislav N. aka pztrn

import argparse
import os

class File_Size_Monitor:
    def __init__(self):
        # Human_readable value in megabytes.
        self.human_readable = 0
        
        self.parse_args()
        
        self.alert_name = "File Size".upper()
        if self.args.ALERT_NAME:
            self.alert_name = self.args.ALERT_NAME.upper()
        
        self.check_size()
        self.compare_sizes()
        
    def check_size(self):
        """
        Checks size of file.
        """
        if self.args.FILE:
            self.human_readable = self.humanize_bytes(os.path.getsize(self.args.FILE))
        else:
            print("No file specified")
            exit(2)
            
    def compare_sizes(self):
        """
        Compare sizes against given values and return approriate
        message and exitcode.
        """
        if self.human_readable < self.args.WARNING:
            print("{0} OK - {1} size is {2} Mbytes".format(self.alert_name, self.args.FILE, self.human_readable))
        elif self.human_readable >= self.args.WARNING and self.human_readable <= self.args.CRITICAL:
            print("{0} WARNING - {1} size is {2} Mbytes".format(self.alert_name, self.args.FILE, self.human_readable))
            exit(1)
        elif self.human_readable >= self.args.CRITICAL:
            print("{0} CRITICAL - {1} size is {2} Mbytes".format(self.alert_name, self.args.FILE, self.human_readable))
            exit(2)
            
    def humanize_bytes(self, bytes):
        """
        Make bytes quantity be human-readable.
        """
        if bytes > 1024:
            bytes = int(bytes / 1024)
            if bytes > 1024:
                bytes = int(bytes / 1024)
                
        # At this point we got megabytes, so we are returning it.
        return bytes

    def parse_args(self):
        """
        Parse commandline arguments
        """
        opts = argparse.ArgumentParser(description='File size monitor')
        opts.add_argument("-f", help="File name to check", metavar="FILE", action="store", dest="FILE")
        opts.add_argument("-w", help="Warning value, in megabytes (default - 100)", metavar="WARN_VALUE", action="store", dest="WARNING", nargs='?', const=1, type=int, default=100)
        opts.add_argument("-c", help="Critical value, in megabytes (default - 150)", metavar="CRIT_VALUE", action="store", dest="CRITICAL", nargs='?', const=1, type=int, default=150)
        opts.add_argument("-n", help="Alert name", metavar="ALERT_NAME", action="store", dest="ALERT_NAME")
        self.args = opts.parse_args()

if __name__ == "__main__":
    File_Size_Monitor()
