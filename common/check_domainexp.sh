#!/bin/bash

# Domain expiration checker.
# Part of pztrn's Icinga additions.
# Copyright (c) 2013 - 2014, Stanislav N. aka pztrn

# Getting domain information.
function get_info() {
    domaininfo=$(${whois} ${domain})
    # Getting zone information. This is neccessary, because some zones
    # may have different substring for domain expiratin value.
    zone=`echo $domain | cut -d "." -f 2`
    if [ $zone == "ru" ]; then
        expire=`echo $domaininfo | grep "paid-till:"| awk -F"till:" '{print $2}' | cut -d " " -f 2`
    elif [ $zone == "org" ]; then
        expire=`echo $domaininfo | awk {' print $15 '} | cut -d "T" -f 1`
    elif [ $zone == "so" ]; then
        expire=`echo $domaininfo | awk {' print $11 '} | cut -d ":" -f 2 | cut -d "T" -f 1`
    elif [ $zone == "com" ]; then
        #echo $domaininfo
        expire=`echo -e ${domaininfo} | grep "Registrar Registration Expiration" | awk {' print $448 '} | cut -d "T" -f 1`
        echo $expire
    else
        echo "Unsupported zone: ${zone}"
        exit 3
    fi
}

# Dates compare.
function compare_dates() {
    # Try to replace dots with dashes, if present.
    expire=$(echo $expire | sed -e "s/\./\-/g")
    expire=`date -d "$expire" -u +"%s"`
    curdate=`date +"%s"`
    expire=$[ $expire-$curdate ]
    expire=$[ $expire / 60 / 60 / 24 ]
    #echo "$domain expires within $expire days"

    # Compare dates and produce exitcodes.
    if [ $expire -le $warn ]; then
        if [ $expire -le $crit ]; then
            echo "DOMEXPIRY CRITICAL: $domain will expire within $expire days"
            exit 2
        else
            echo "DOMEXPIRY WARNING: $domain will expire within $expire days"
            exit 1
        fi
    else
        echo "DOMEXPIRY OK: $domain will expire within $expire days"
        exit 0
    fi
}

function help() {
    echo "Domain expiration checker for Nagios/Icinga.
Checks domains in these zones:

    com, org, ru, so

Usage:
    mon_domainexp.sh [domain] [warn] [crit]

Available options:
    [domain]        Domain to check.
    [warn]          Produce warning if domain will expire in this days.
    [crit]          Produce critical if domain will expire in this days."
}

# Executes some preparation actions, e.g. searching for whois program.
function prepare() {
    whois_raw=`whereis whois`
    if [ ${#whois_raw} -lt 10 ]; then
        echo "Whois program not found! Cannot continue!"
        exit 3
    else
        whois=`echo ${whois_raw} | awk {' print $2 '}`
    fi
}

case $1 in
    -h)
        help
    ;;
    *)
        domain=$1
        warn=$2
        crit=$3
        prepare
        get_info
        compare_dates
esac
