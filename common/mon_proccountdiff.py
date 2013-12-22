#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Monitoring script for processes count.
# Part of pztrn's Icinga additions.
# Copyright (c) 2013, Stanislav N. aka pztrn

import sys
import argparse
import subprocess

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
                
        if (not self.args.PROCESS_ONE and not self.args.PROCESS_TWO) or (self.args.PROCESS_ONE and not self.args.PROCESS_TWO) or (not self.args.PROCESS_ONE and self.args.PROCESS_TWO):
            print("Both process names required!")
            exit(20)
            
        # If PSUTIL and PSAX parameters set - forcing PSUTIL one.
        if not self.args.PSAX and not self.args.PSUTIL:
            self.args.PSUTIL = True
                
        # Process name to count.
        # Counting process instances.
        count_proc1 = 0
        count_proc2 = 0
        
        if self.args.PSAX and not self.args.PSUTIL:
            p = subprocess.Popen(["ps", "ax"], stdout = subprocess.PIPE)
            data = p.communicate()[0]
            data = str(data).split(r"\n")
        elif not self.args.PSAX and self.args.PSUTIL:
            try:
                import psutil
            except:
                print("PSUtil module not installed!")
                exit(10)
            data = []
            for item in psutil.process_iter():
                data.append(item.name)
        else:
            print("Error while trying to get processes listing - you should use only one method.")
        
        # Alert name replacer.
        if self.args.ALERT_NAME:
            alert_name = self.args.ALERT_NAME.upper()
        else:
            alert_name = "PROCS DIFF"
            
        # Iterating thru processes to get them counted.
        for item in data:
            if self.args.PROCESS_ONE in item and not "mon_proccountdiff" in item:
                count_proc1 += 1
            elif self.args.PROCESS_TWO in item and not "mon_proccountdiff" in item:
                count_proc2 += 1
        
        # Getting difference.
        diff = count_proc1 - count_proc2
        
        if do_criticals and diff <= CRIT_VALUE:
            print(alert_name + " CRITICAL: difference is {0} ({1} - {2}, {3} - {4})".format(diff, self.args.PROCESS_ONE, count_proc1, self.args.PROCESS_TWO, count_proc2))
            exit(2)
        elif do_warnings and diff < CRIT_VALUE and diff >= WARN_VALUE:
            print(alert_name + " WARNING: difference is {0} ({1} - {2}, {3} - {4})".format(diff, self.args.PROCESS_ONE, count_proc1, self.args.PROCESS_TWO, count_proc2))
            exit(1)
        else:
            print(alert_name + " OK: difference is {0} ({1} - {2}, {3} - {4})".format(diff, self.args.PROCESS_ONE, count_proc1, self.args.PROCESS_TWO, count_proc2))
            exit(0)
        
    def parse_args(self):
        """
        Parse commandline arguments
        """
        opts = argparse.ArgumentParser(description='Process count difference monitor', epilog="Monitor processes difference by count. Each process will be counted, and result will be 'process1 - process2' instances. E.g. process1 is 'ssh', process2 is 'zsh', process1 counted 6 times, process2 - 3 times. Difference will be 3.")
        opts.add_argument("-1", help="First process name", metavar="PROCESS_ONE", action="store", dest="PROCESS_ONE")
        opts.add_argument("-2", help="Second process name", metavar="PROCESS_TWO", action="store", dest="PROCESS_TWO")
        opts.add_argument("-p", help="Use 'ps ax' for process listing. Will search not only thru binaries names, but also thru parameters.", action="store_true", dest="PSAX")
        opts.add_argument("-u", help="Use 'psutil' for process listing. Will search only thru binaries names.", action="store_true", dest="PSUTIL")
        opts.add_argument("-w", help="Warning difference", metavar="WARN_VALUE", action="store", dest="WARNING")
        opts.add_argument("-c", help="Critical difference", metavar="CRIT_VALUE", action="store", dest="CRITICAL")
        opts.add_argument("-n", help="Alert name (for prettifing output)", metavar="ALERT_NAME", action="store", dest="ALERT_NAME")
        self.args = opts.parse_args()
        
if __name__ == "__main__":
    Process_Monitor()
