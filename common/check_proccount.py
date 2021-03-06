#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Monitoring script for processes count.
# Part of pztrn's Icinga additions.
# Copyright (c) 2013 - 2016, Stanislav N. aka pztrn

import argparse
import subprocess

try:
    import psutil
except:
    print("PSUtil module not installed!")
    exit(10)

class Process_Monitor:
    def __init__(self):
        # Warning may not be needed.
        do_warnings = False
        # Critical may not be needed.
        do_criticals = False

        self.parse_args()
        if self.args.WARNING:
            do_warnings = True
            try:
                WARN_VALUE = int(self.args.WARNING)
            except:
                print("Warning value must be an integer!")
                exit(10)
            # We should force CRIT_VALUE as 0.
            # For fuck's sake.
            CRIT_VALUE = 0

        if self.args.CRITICAL:
            do_criticals = True
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
                if process.name == self.args.PROCESS and not "mon_proccount" in process.name:
                    count += 1

        elif self.args.PARM:
            opt = self.args.PARM
            p = subprocess.Popen(["ps", "ax"], stdout = subprocess.PIPE)
            data = p.communicate()[0]
            data = str(data).split(r"\n")
            for item in data:
                if self.args.PARM in item and not "mon_proccount" in item:
                    #print(item)
                    count += 1

        # Alert name replacer.
        if self.args.ALERT_NAME:
            alert_name = self.args.ALERT_NAME.upper()
        else:
            alert_name = opt.upper()

        if do_criticals and count <= CRIT_VALUE:
            print(alert_name + " CRITICAL: {0} instances running".format(count))
            exit(2)
        elif do_warnings and count > CRIT_VALUE and count <= WARN_VALUE:
            print(alert_name + " WARNING: {0} instances running".format(count))
            exit(1)
        else:
            print(alert_name + " OK: {0} instances running".format(count))
            exit(0)

    def parse_args(self):
        """
        Parse commandline arguments
        """
        opts = argparse.ArgumentParser(description='Process count monitor', epilog="Monitor processes by count.")
        opts.add_argument("-p", help="Process name", metavar="PROCESSNAME", action="store", dest="PROCESS")
        opts.add_argument("-o", help="Process parameter", metavar="PROCESSPARAM", action="store", dest="PARM")
        opts.add_argument("-w", help="Warning value", metavar="WARN_VALUE", action="store", dest="WARNING")
        opts.add_argument("-c", help="Critical value", metavar="CRIT_VALUE", action="store", dest="CRITICAL")
        opts.add_argument("-n", help="Alert name", metavar="ALERT_NAME", action="store", dest="ALERT_NAME")
        self.args = opts.parse_args()

if __name__ == "__main__":
    Process_Monitor()
