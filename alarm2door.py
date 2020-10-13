from gpiozero import Button
import requests
import hashlib
import xml.etree.ElementTree as ET
import time
from multiprocessing.pool import ThreadPool as Pool
import traceback
import datetime
import boto3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# this is a systemd service for opening all the doors when the alarm goes off using a raspberry pin
# it will hold the door open until the button is pressed to resume normal door function

username = 'admin'
password = 'xxxxxxx'
to_email = ['xxxxxxx@gmail.com'] # a list of emails
from_email = 'alarm2door@xxxxxxx.com'
AWS_ACCESS_KEY_ID = "xxxxxxx"
AWS_SECRET_ACCESS_KEY = "xxxxxxxxxxxxx"

pin = '1' # the grandstream device unlock security pin number
site='gastro'
sleep = 10 # equal the "Unlock Holding Time" in "Door System Settings"
test_mode = True
email_startup = True


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

sesClient = boto3.client( 'ses', 
	aws_access_key_id=AWS_ACCESS_KEY_ID,
	aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
	region_name='us-east-1' )

if email_startup:
	sesClient.send_email(
				Source = from_email,
				Destination={'ToAddresses': to_email},
				Message={	'Body': {
								'Text': {'Data': "The service was started at %s.\nclose-trigger engaged: %s\nopen-trigger engaged: %s" % (datetime.datetime.now(), close_button.is_pressed, open_button.is_pressed)},
							},
							'Subject': {'Data': "ALARM2DOOR: service started" }
						}
			)

keep_doors_open = False

def main():
	print('alarm2door is now running')
	print('for support contact chris@alexspc.com')

	close_button.when_pressed = close_doors
	open_button.when_pressed = open_doors

	while True:
		if keep_doors_open and not test_mode:
			p = Pool(len(endpoints))
			p.map(openDoor, endpoints)
			p.close()
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

def emailNotify(state):
	try:
		sesClient.send_email(
					Source = from_email,
					Destination={'ToAddresses': to_email},
					Message={	'Body': {
									'Text': {'Data': "The alarm at %s was toggled at %s the doors are now %s. (this_is_just_a_drill=%s)" % (site, datetime.datetime.now(), state, test_mode)},
								},
								'Subject': {'Data': "ALARM2DOOR: %s doors %s" % (site, state)}
							}
				)
	except Exception as e:
		print("Exception in emailNotify(): " + e)

def open_doors():
	global keep_doors_open
	keep_doors_open = True
	print("open_doors() triggered")
	emailNotify('unlocked')

def close_doors():
	global keep_doors_open
	keep_doors_open = False
	print("close_doors() triggered")
	emailNotify('locked')

if __name__ == '__main__':
	main()

