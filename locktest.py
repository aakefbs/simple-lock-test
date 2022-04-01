#!/usr/bin/env python3

import os, sys
import fcntl
import argparse
import time
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("path")
parser.add_argument("cmd")
parser.add_argument("sleep_time")
parser.add_argument("lock_type") # lockf or flock
# XXX: Add argument for the range!

#pdb.set_trace()

# parse the arguments
args = parser.parse_args()

class path_lock:
    def __init__(self, path, cmd_str):
        self.path    = path
        self.cmd_str = cmd_str

        # XXX Needs command line arguments for this
        self.len    = 0
        self.start  = 0
        self.whence = 0

        self.is_flock = -1 # not set

        self.fd = self.path_open(path)
        self.cmd = self.get_cmd(cmd_str)

    def path_open(self, path):
        try:
            fd = open(path, 'r+')
        except OSError as error:
            sys.exit("Failed to open '" + path + "': " + str(error))
            
        return fd


    def get_cmd(self, cmd_str):
        cmd = -1
        if   (cmd_str == "LOCK_EX"):
            cmd = fcntl.LOCK_EX
        elif (cmd_str == "LOCK_SH"):
            cmd = fcntl.LOCK_SH
        elif (cmd_str == "LOCK_UN"):
            cmd = fcntl.LOCK_UN
        else:
            sys.exit("Failed to convert locktype: " + lock_type_str)

        return cmd

    def flock(self, is_unlock = False):

        self.is_flock = 1
    
        try:
            fcntl.flock(self.fd, self.cmd)
        except OSError as error:
            sys.exit("Failed to flock " + self.path + ": " + str(error))

        lock_str = "flock-locked"
        if (is_unlock):
            lock_str = "flock-unlocked"

        print(lock_str + self.path + " with " + self.cmd_str + 
              "(" + str(self.cmd) + ")")

    def lockf(self, is_unlock = False):

        self.is_flock = 0

        try:
            fcntl.lockf(self.fd, self.cmd, self.len, self.start, self.whence)
        except OSError as error:
            sys.exit("Failed to flock " + self.path + ": " + str(error))

        lock_str = "lockf-locked"
        if (is_unlock):
            lock_str = "lockf-unlocked"

        # XXX: Add ranges
        print(lock_str + self.path + " with " + self.cmd_str +
              "(" + str(self.cmd) + ")")

    def unlock(self):
        if (self.is_flock == -1):
            sys.exit("File not locked, cannot use this unlock method")

        print("Unlocking " + self.path)
        cmd_saved = self.cmd # backup
        self.cmd = fcntl.LOCK_UN
        if (self.is_flock == 1):
            self.flock(is_unlock = True)
        else:
            self.lockf(is_unlock = True)
        self.cmd = cmd_saved # restore

        self.is_flock = -1


path_lock_obj = path_lock(args.path, args.cmd)

if (args.lock_type == "flock"):
    path_lock_obj.flock()
elif(args.lock_type  == "lockf"):
    path_lock_obj.lockf()
else:
    sys.exit("Invalid lock-type: '" + args.lock_type + "'")

now = datetime.now()
time_str = now.strftime("%d/%m/%Y %H:%M:%S")
print(time_str + " Holding the lock for " + args.sleep_time + "s")
time.sleep(int(args.sleep_time))

path_lock_obj.unlock()
