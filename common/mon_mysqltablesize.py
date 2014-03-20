#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Monitoring script MySQL database size.
# Part of pztrn's Icinga additions.
# Copyright (c) 2013 - 2014, Stanislav N. aka pztrn

import argparse
import pymysql

class MySQL_Table_Size_Monitor:
    def __init__(self):
        self.parse_args()
        
        self.alert_name = "MySQL Table Size".upper()
        if self.args.ALERT_NAME:
            self.alert_name = self.args.ALERT_NAME.upper()
        
        self.connect_to_db()
        self.get_table_size()
        self.compare()
        
    def connect_to_db(self):
        """
        Connect to database.
        """
        try:
            self.connection = pymysql.connect(host = self.args.HOST, user = self.args.USER, passwd = self.args.PASSWORD, use_unicode = True)
            self.database = self.connection.cursor()
        except pymysql.err.OperationalError as e:
            print("{0} CRITICAL - {1}".format(self.alert_name, e))
            exit(2)
        
    def get_table_size(self):
        """
        Gets table size from database.
        """
        self.table_size = self.database.execute("SELECT SUM(data_length + index_length) / 1024 / 1024 AS '' FROM information_schema.TABLES WHERE table_schema=%s", self.args.DATABASE)
        self.table_size = self.database.fetchone()[0]
        self.table_size = float("%0.2f" % self.table_size)
        
    def compare(self):
        """
        Compare and decide what to do.
        """
        if self.table_size < float(self.args.WARNING):
            print("{0} OK - '{1}' size is {2}M".format(self.alert_name, self.args.DATABASE, self.table_size))
            exit(0)
        elif float(self.args.WARNING) <= self.table_size and self.table_size <= float(self.args.CRITICAL):
            print("{0} WARNING - '{1}' size is {2}M".format(self.alert_name, self.args.DATABASE, self.table_size))
            exit(1)
        else:
            print("{0} CRITICAL - '{1}' size is {2}M".format(self.alert_name, self.args.DATABASE, self.table_size))
            exit(2)
        
    def parse_args(self):
        """
        Parse commandline arguments
        """
        opts = argparse.ArgumentParser(description='Database size monitor')
        opts.add_argument("-H", help="MySQL host", metavar="HOST", action="store", dest="HOST")
        opts.add_argument("-u", help="MySQL user", metavar="USER", action="store", dest="USER")
        opts.add_argument("-p", help="MySQL password", metavar="PASSWORD", action="store", dest="PASSWORD")
        opts.add_argument("-d", help="Database name", metavar="DATABASE", action="store", dest="DATABASE")
        opts.add_argument("-w", help="Warning value", metavar="WARN_VALUE", action="store", dest="WARNING")
        opts.add_argument("-c", help="Critical value", metavar="CRIT_VALUE", action="store", dest="CRITICAL")
        opts.add_argument("-n", help="Alert name", metavar="ALERT_NAME", action="store", dest="ALERT_NAME")
        self.args = opts.parse_args()

if __name__ == "__main__":
    MySQL_Table_Size_Monitor()
