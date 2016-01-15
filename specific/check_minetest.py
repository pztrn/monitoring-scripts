#!/usr/bin/env python3

# Minetest monitoring script.
# Part of pztrn's Icinga additions.
# Copyright (c) 2013 - 2016, Stanislav N. aka pztrn

# Log file
logfile = "/data/programs/minetest/logs/minetest_restarts.log"

filedata = open(logfile).read()

if len(filedata) > 0:
    filedata = filedata[:-1].split("\n")
    lines = 0
    for line in filedata:
        lines += 1

    filedata = " || ".join(filedata)
    if lines > 10:
        print("MINETEST CRITICAL - too many restarts ({0}): {1}".format(lines, filedata))
        exit(2)
    else:
        print("MINETEST WARNING - {0} restarts: {1}".format(lines, filedata))
        exit(1)
else:
    print("MINETEST OK - no restarts")
    exit()
