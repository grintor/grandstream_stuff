from gpiozero import Button
import requests
import hashlib
import xml.etree.ElementTree as ET
import time
from multiprocessing.pool import ThreadPool as Pool
import traceback

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# this is a systemd service for opening all the doors when the alarm goes off using a raspberry pin
# it will hold the door open until the button is pressed to resume normal door function

password = 'PASSWORD_HERE'
username = 'admin'
pin = '1'
sleep = 10 # equal the "Unlock Holding Time" in "Door System Settings"

endpoints = [
	'https://192.168.1.71',
	'https://192.168.1.72',
	'https://192.168.1.73',
	'https://192.168.1.74',
	'https://192.168.1.75',
	'https://192.168.1.76',
	'https://192.168.1.77',
	'https://192.168.1.78',
	'https://192.168.1.79',
	'https://192.168.1.80',
	'https://192.168.1.81',
	'https://192.168.1.82',
	'https://192.168.1.83',
	'https://192.168.1.84',
	'https://192.168.1.85',
	'https://192.168.1.86',
	'https://192.168.1.87',
	'https://192.168.1.88',
	'https://192.168.1.89',
	'https://192.168.1.90',
	'https://192.168.1.91',
	'https://192.168.1.92',
	'https://192.168.1.93',
	'https://192.168.1.94',
	'https://192.168.1.95',
	'https://192.168.1.96',
	'https://192.168.1.97',
	'https://192.168.1.98',
	'https://192.168.1.99',
	'https://192.168.1.100',
	'https://192.168.1.101',
	'https://192.168.1.102',
	'https://192.168.1.103',
	'https://192.168.1.104',
	'https://192.168.1.105',
]


# jump to ground (pins 6, 14, 20, 30, 34, 9, 25, or 39) to engage

close_button = Button(2) # pin 3
open_button = Button(3) # pin 5

keep_doors_open = False

def main():
	print('alarm2door is now running')
	print('for support contact chris@alexspc.com')

	close_button.when_pressed = close_doors
	open_button.when_pressed = open_doors

	while True:
		if keep_doors_open:
			p = Pool(len(endpoints))
			p.map(openDoor, endpoints)
			time.sleep(sleep)
		time.sleep(1)


def openDoor(endpoint):
	try:
		result = requests.get('%s/goform/apicmd?cmd=0&user=%s' % (endpoint, username), verify=False, timeout = sleep/2)

		tree = ET.fromstring(result.text)
		idcode = tree.find('IDCode').text

		challengecode = tree.find('ChallengeCode').text

		m = hashlib.md5()
		m.update(("%s:%s:%s" % (challengecode, pin, password)).encode())
		authcode = m.hexdigest()

		result = requests.get('%s/goform/apicmd?cmd=1&user=%s&authcode=%s&idcode=%s&type=1' % (endpoint, username, authcode, idcode), verify=False, timeout = sleep/2)
		tree = ET.fromstring(result.text)
		ResCode = int(tree.find('ResCode').text)
		RetMsg = tree.find('RetMsg').text
		if ResCode != 0:
			print ("%s: %s" % (endpoint, RetMsg))
		else:
			pass # comment out the print below to not print success messages
			print ("%s: %s" % (endpoint, RetMsg))

	except AttributeError as err:
		print ("%s\n%s\n%s" % (endpoint, err, result.text))
	except ET.ParseError as err:
		print ("%s\n%s\n%s" % (endpoint, err, result.text))
	except:
		print ("%s\n%s" % (endpoint, traceback.format_exc()))

def open_doors():
	global keep_doors_open
	keep_doors_open = True

def close_doors():
	global keep_doors_open
	keep_doors_open = False


if __name__ == '__main__':
	main()

