#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Monitoring script for processes count.
# Part of pztrn's Icinga additions.
# Copyright (c) 2013, Stanislav N. aka pztrn

import sys
import argparse
import subprocess

try:
    import psutil
except:
    print("PSUtil module not installed!")
    exit(10)

class Process_Monitor:
    def __init__(self):
        self.parse_args()
        try:
            WARN_VALUE = int(self.args.WARNING)
        except:
            print("Warning value must be an integer!")
            exit(10)
            
        try:
            CRIT_VALUE = int(self.args.CRITICAL)
        except:
            print("Critical value must be an integer!")
            exit(10)
        # Process name to count.
        # Counting process instances.
        count = 0
        if self.args.PROCESS:
            opt = self.args.PROCESS
            for process in psutil.process_iter():
                if process.name == self.args.PROCESS:
                    count += 1
        
        if self.args.PARM:
            opt = self.args.PARM
            p = subprocess.Popen(["ps", "ax"], stdout = subprocess.PIPE)
            data = p.communicate()[0]
            data = str(data).split(r"\n")
            for item in data:
                if self.args.PARM in item:
                    count += 1
                    
            # One of detected values - ps itself.
            count -= 1
                
        if count <= CRIT_VALUE:
            print(opt.upper() + " CRITICAL: {0} instances running".format(count))
            exit(2)
        elif count > CRIT_VALUE and count <= WARN_VALUE:
            print(opt.upper() + " WARNING: {0} instances running".format(count))
            exit(1)
        else:
            print(opt.upper() + " OK: {0} instances running".format(count))
            exit(0)
        
    def parse_args(self):
        """
        Parse commandline arguments
        """
        opts = argparse.ArgumentParser(description='Process count monitor', epilog="Monitor processes by count.")
        opts.add_argument("-p", help="Process name", metavar="PROCESSNAME", action="store", dest="PROCESS")
        opts.add_argument("-o", help="Process parameter", metavar="PROCESSNAME", action="store", dest="PARM")
        opts.add_argument("-w", help="Warning value", metavar="WARN_VALUE", action="store", dest="WARNING")
        opts.add_argument("-c", help="Critical value", metavar="CRIT_VALUE", action="store", dest="CRITICAL")
        self.args = opts.parse_args()
        
if __name__ == "__main__":
    Process_Monitor()
