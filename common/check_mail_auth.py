#!/usr/bin/env python3

# Mail authentication check script for Nagios/Icinga
# Copyright (c) 2015 Stanislav N. aka pztrn <pztrn at pztrn dot name>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import imaplib
import json
import os
import smtplib
import socket
import sys

# Help text
HELP_TEXT = """Mail authentication check script for Nagios/Icinga
Copyright (c) 2015 Stanislav N. aka pztrn <pztrn at pztrn dot name>

Syntax:

    check_mail_auth.py [params] ...

Acceptable parameters:

    Common:
        -h                  This help.

    Connection related:
        -cc [seconds]       Critical value for server response.
        -ct [imap/smtp]     Connection type.

    Mail related:
        -mc [conn_name]     Connection name to use from configuration file.
        -mH [domain_or_ip]  Host name or IP address of mail server.
        -mp [password]      Password for user to check.
        -mP [port]          Port to use.
        -mu [username]      Username for check.
        -ms                 Use ssl
        -mt                 Use TLS"""

class Check_Mail_Auth:
    def __init__(self):
        # Defaulting some configuration variables.
        self.__config = {
            # Main configuration.
            "main": {
                # Defaulting debug level to 0. We don't need debug by default.
                "debug"             : 0
            },
            # This dictionary will be filled with connection-specific
            # options.
            "connection" : {},
            # This dictionary will be filled with passed credentials.
            "credentials": {}
        }

    def check_mail_auth(self):
        """
        Actual for mail authorization. If everything went OK: exitcode 0. If
        something failed: exitcode 2.
        """
        self.log(1, "Checking credentials...")
        self.log(1, "Credentials length: {0}".format(len(self.__config["credentials"])))
        if len(self.__config["credentials"]) == 0:
            self.log(0, "!!! ERROR: no credentials specified.")
            exit(3)

        conn_type = self.__config["main"]["connection_type"]
        self.log(1, "Connection type: {0}".format(conn_type))

        if not "connection_to_use" in self.__config["main"]:
            conn_data = self.__config["credentials"]["from_CLI"]
        else:
            conn_data = self.__config["credentials"][self.__config["main"]["connection_to_use"]]

        if conn_type == "imap":
            self.__check_imap(conn_data)
        elif conn_type == "smtp":
            self.__check_smtp(conn_data)
        else:
            self.log(0, "!!! ERROR: unsupported connection type: '{0}'".format(conn_type))

    def log(self, level, data):
        """
        Simple logging method. It respects:

            * DEBUG configuration variable
            * DEBUG environment variable
            * DEBUG CLI parameter

        Note, that environment variable WILL OVERRIDE configuration value in
        __parse_config() method, and CLI parameter will override everything!
        """
        if level == 0:
            print(data)
        elif level > 0 and self.__config["main"]["debug"] != 0:
            print("[DEBUG] {0}".format(data))

    def parse_parameters(self):
        """
        Starting point for parameters parsing. It will launch separate
        methods for:

            * Loading configuration values, if present
            * Parsing CLI parameters

        Note, that CLI parameters will override configuration variables!
        """
        self.__parse_config()
        self.__parse_env()
        self.__parse_CLI()

    def show_help(self):
        """
        Shows help :).
        """
        print(HELP_TEXT)

    def __check_imap(self, conn_data):
        """
        Checks IMAP server.
        """
        self.log(1, "Trying to connect to IMAP server...")
        if not "port" in conn_data:
            if conn_data["ssl"]:
                self.log(1, "Port wasn't specified. Will use 993 for SSL.")
                conn_data["port"] = 993
            if conn_data["tls"]:
                self.log(1, "Port wasn't specified. Will use 143 for TLS.")
                conn_data["port"] = 143
            if not conn_data["ssl"] and not conn_data["tls"]:
                self.log(1, "Port wasn't specified. Will use 143 for IMAP.")
                self.log(1, "! WARN: will use insecure connection! ")
                conn_data["port"] = 143

        # IMAP cannot use timeouts, so we set script-wide socket timeout.
        socket.setdefaulttimeout(self.__config["main"]["timeout"])

        try:
            if not conn_data["ssl"]:
                self.log(1, "Using non-SSL handler.")
                s = imaplib.IMAP4(host = conn_data["hostname"], port = conn_data["port"])
            else:
                self.log(1, "Using SSL handler.")
                s = imaplib.IMAP4_SSL(host = conn_data["hostname"], port = conn_data["port"])
        except socket.timeout as e:
            self.log(0, "CRITICAL - Login operation timed out for connection '{0}' (host: {1}, user: {2}, type {3}) was successful".format(self.__config["main"]["connection_to_use"], conn_data["hostname"], conn_data["username"], self.__config["main"]["connection_type"]))

        if conn_data["tls"]:
            self.log(1, "Starting TLS negotiation...")
            s.starttls()

        self.log(1, "Connetion established.")

        try:
            self.log(1, "Logging in...")
            s.login(conn_data["username"], conn_data["password"])
            self.log(1, "Issuing select()...")
            s.select()
        except socket.timeout:
            self.log(0, "CRITICAL - Login operation timed out for connection '{0}' (host: {1}, user: {2}, type {3}) was successful".format(self.__config["main"]["connection_to_use"], conn_data["hostname"], conn_data["username"], self.__config["main"]["connection_type"]))

        self.log(0, "OK - Authentication for connection '{0}' (host: {1}, user: {2}, type {3}) was successful".format(self.__config["main"]["connection_to_use"], conn_data["hostname"], conn_data["username"], self.__config["main"]["connection_type"]))
        s.logout()

    def __check_smtp(self, conn_data):
        """
        Checks SMTP server.
        """
        self.log(1, "Trying to connect to SMTP server...")

        if not "port" in conn_data:
            if conn_data["ssl"]:
                self.log(1, "Port wasn't specified. Will use 587 for SSL.")
                conn_data["port"] = 587
            if conn_data["tls"]:
                self.log(1, "Port wasn't specified. Will use 25 for TLS.")
                conn_data["port"] = 25
            if not conn_data["ssl"] and not conn_data["tls"]:
                self.log(1, "Port wasn't specified. Will use 25 for SMTP.")
                self.log(1, "! WARN: will use insecure connection! ")
                conn_data["port"] = 25

        try:
            if not conn_data["ssl"]:
                self.log(1, "Using non-SSL handler.")
                s = smtplib.SMTP(host = conn_data["hostname"], port = conn_data["port"], timeout = self.__config["main"]["timeout"])
            else:
                self.log(1, "Using SSL handler.")
                s = smtplib.SMTP_SSL(host = conn_data["hostname"], port = conn_data["port"], timeout = self.__config["main"]["timeout"])
        except socket.timeout as e:
            self.log(0, "CRITICAL - Socket timeout for connection '{0}' (host: {1}, user: {2}, type {3})".format(self.__config["main"]["connection_to_use"], conn_data["hostname"], conn_data["username"], self.__config["main"]["connection_type"]))
            exit(2)
        #s.connect()
        s.set_debuglevel(self.__config["main"]["debug"])
        self.log(1, "Connection established.")

        if conn_data["tls"]:
            self.log(1, "Starting TLS negotiation...")
            s.starttls()

        s.ehlo_or_helo_if_needed()
        #s.esmtp_features["auth"]="LOGIN PLAIN"
        try:
            s.login(conn_data["username"], conn_data["password"])
        except smtplib.SMTPAuthenticationError as e:
            self.log(0, "CRITICAL - SMTP authentication for '{0}' rejected!".format(conn_data["username"]))
            exit(2)
        except smtplib.SMTPException as e:
            self.log(0, "CRITICAL - No suitable auth methods found for connection '{0}'".format(self.__config["main"]["connection_to_use"]))
            exit(2)

        self.log(0, "OK - Authentication for connection '{0}' (host: {1}, user: {2}, type {3}) was successful".format(self.__config["main"]["connection_to_use"], conn_data["hostname"], conn_data["username"], self.__config["main"]["connection_type"]))
        s.quit()

    def __parse_CLI(self):
        """
        This method parses CLI parameters.
        """
        self.log(1, "Parsing CLI parameters...")
        params = sys.argv[1:]
        if len(params) == 0 or "-h" in params:
            self.show_help()

        # Parsing credentials data.
        if "-mH" in params:
            self.log(1, "Detected mail server parameters in CLI!")
            self.__config["credentials"]["from_CLI"] = {}
            self.__config["credentials"]["from_CLI"]["hostname"] = params[params.index("-mH") + 1]

            # Password for user.
            if "-mp" in params:
                self.__config["credentials"]["from_CLI"]["password"] = params[params.index("-mp") + 1]
            else:
                self.log(0, "!!! ERROR: password for user not specified!")
                exit(3)

            # Username.
            if "-mu" in params:
                self.__config["credentials"]["from_CLI"]["username"] = params[params.index("-mu") + 1]
            else:
                self.log(0, "!!! ERROR: user not specified!")
                exit(3)

            # SSL trigger.
            if "-ms" in params:
                self.log(1, "Will use SSL.")
                self.__config["credentials"]["from_CLI"]["ssl"] = 1
            else:
                self.__config["credentials"]["from_CLI"]["ssl"] = 0

            # TLS trigger.
            if "-mt" in params:
                self.log(1, "Will use TLS")
                self.__config["credentials"]["from_CLI"]["tls"] = 1
            else:
                self.__config["credentials"]["from_CLI"]["tls"] = 0

            self.log(1, "Credentials parsed:")
            self.log(1, self.__config["credentials"])

        # What connection to use? If we pass "-mc conn_name" - it will be used.
        # If nothing was passed no "-mc" and no credentials was passed to
        # approriate parameters - exit.
        if "-mc" in params:
            self.__config["main"]["connection_to_use"] = params[params.index("-mc") + 1]
        else:
            if not "from_CLI" in self.__config["credentials"]:
                self.log(0, "!!! ERROR: no credentials was supplied for checking!")
                exit(3)
            else:
                self.__config["main"]["connection_to_use"] = "from_CLI"

        # Connection timeout.
        if "-cc" in params:
            try:
                timeout = int(params[params.index("-cc") + 1])
            except:
                self.log(1, "! WARN: passed parameter to -cc wasn't an integer, defaulting timeout to 10 seconds")
                timeout = 10

            if timeout == "0":
                self.log(1, "! WARN: connection timeout cannot be 0, defaulting to 10 seconds!")
                timeout = 10

            self.log(1, "Connection timeout set: {0}".format(timeout))
            self.__config["main"]["timeout"] = timeout
        else:
            if not "timeout" in self.__config["credentials"][self.__config["main"]["connection_to_use"]]:
                self.log(1, "! WARN: timeout wasn't specified - defaulting to 10 seconds.")
                self.__config["main"]["timeout"] = 10
            else:
                self.__config["main"]["timeout"] = self.__config["credentials"][self.__config["main"]["connection_to_use"]]["timeout"]
                self.log(1, "Timeout value taken from connection configuration file: {0} seconds".format(self.__config["main"]["timeout"]))

        # Connection type.
        if "-ct" in params:
            conn_type = params[params.index("-ct") + 1]
            self.log(1, "Connection type: {0}".format(conn_type))
            self.__config["main"]["connection_type"] = conn_type.lower()
            if "-mP" in params:
                try:
                    port = int(params[params.index("-mP") + 1])
                except:
                    self.log(0, "!!! ERROR: passed port value isn't an integer!")
                    exit(3)
                self.log(1, "Will use port {0}".format(port))
                self.__config["credentials"]["from_CLI"]["port"] = port
            else:
                self.log(1, "! WARN: port wasn't specified: will use default.")
        else:
            if not "connection_type" in self.__config["credentials"][self.__config["main"]["connection_to_use"]]:
                self.log(1, "! WARN: connection type wasn't specified - defaulting to IMAP.")
                self.__config["main"]["connection_type"] = "imap"
            else:
                self.__config["main"]["connection_type"] = self.__config["credentials"][self.__config["main"]["connection_to_use"]]["connection_type"]
                self.log(1, "Connection type taken from connection configuration file: {0}".format(self.__config["main"]["connection_type"]))

    def __parse_config(self):
        """
        This method parses configuration file into dictionary.
        """
        config_path = "/etc/nagios/plugins/"
        # Locate all configuration files for this script.
        # Return if configuration path doesn't exist.
        try:
            configs = os.listdir(config_path)
        except FileNotFoundError as e:
            return
        # Read all configuration files and update self.__config dictionary.
        for config in configs:
            raw_data = open(os.path.join(config_path, config), "r").read()
            data = json.loads(raw_data)
            self.__config.update(data)

    def __parse_env(self):
        """
        This method parses some environment variables and replaces configuration
        values.
        """
        if "DEBUG" in os.environ:
            try:
                self.__config["main"]["debug"] = int(os.environ["DEBUG"])
                self.log(1, "DEBUG overrided to {0}".format(self.__config["main"]["debug"]))
            except:
                print("!!! Failed to convert DEBUG value to integer! This is fatal error!")
                exit(3)

if __name__ == "__main__":
    c = Check_Mail_Auth()
    c.parse_parameters()
    c.check_mail_auth()
