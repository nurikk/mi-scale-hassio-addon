#!/usr/bin/python
# coding: utf-8

import os
import time
import json
import paho.mqtt.client as mqtt
import Xiaomi_Scale_Body_Metrics as XSBM

from bluepy import btle
from datetime import datetime

CONFIG = json.load(open('/data/options.json'))

MISCALE_MAC = CONFIG.get('miscale_mac', '')
MQTT_USERNAME = CONFIG.get('mqtt_username', '')
MQTT_PASSWORD = CONFIG.get('mqtt_password', '')
MQTT_HOST = CONFIG.get('mqtt_host', '127.0.0.1')
MQTT_PORT = CONFIG.get('mqtt_port', 1883)
MQTT_TIMEOUT = CONFIG.get('mqtt_timeout', 60)
MQTT_PREFIX = CONFIG.get('mqtt_prefix', 'miScale')

USERS = CONFIG.get('users', [])

class ScanProcessor():

	def getAge(self, d1):
		if not d1: return
		d1 = datetime.strptime(d1, "%Y-%m-%d")
		d2 = datetime.strptime(datetime.today().strftime('%Y-%m-%d'),'%Y-%m-%d')
		return abs((d2 - d1).days)/365

	def __init__(self):
		self.mqtt_client = None
		self.connected = False
		self._start_client()

	def handleDiscovery(self, dev, isNewDev, isNewData):
		if dev.addr == MISCALE_MAC.lower() and isNewDev:
			for (sdid, _, data) in dev.getScanData():
				### Xiaomi V1 Scale ###
				if data.startswith('1d18') and sdid == 22:
					measunit = data[4:6]
					measured = int((data[8:10] + data[6:8]), 16) * 0.01
					unit = ''

					if measunit.startswith(('03', 'b3')): unit = 'lbs'
					if measunit.startswith(('12', 'b2')): unit = 'jin'
					if measunit.startswith(('22', 'a2')): unit = 'kg' ; measured = measured / 2

					if unit:
						self._publish(round(measured, 2), unit, None, 0)
					else:
						print("Scale is sleeping.")

				### Xiaomi V2 Scale ###
				if data.startswith('1b18') and sdid == 22:
					measunit = data[4:6]
					measured = int((data[28:30] + data[26:28]), 16) * 0.01
					unit = ''

					if measunit == "03": unit = 'lbs'
					if measunit == "02": unit = 'kg' ; measured = measured / 2
					mitdatetime = datetime.strptime(str(int((data[10:12] + data[8:10]), 16)) + " " + str(int((data[12:14]), 16)) +" "+ str(int((data[14:16]), 16)) +" "+ str(int((data[16:18]), 16)) +" "+ str(int((data[18:20]), 16)) +" "+ str(int((data[20:22]), 16)), "%Y %m %d %H %M %S")
					miimpedance = str(int((data[24:26] + data[22:24]), 16))

					if unit:
						self._publish(round(measured, 2), unit, str(mitdatetime), miimpedance)
					else:
						print("Scale is sleeping.")


			if not dev.scanData:
				print ('\t(no data)')


	def _start_client(self):
		self.mqtt_client = mqtt.Client()
		self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

		def _on_connect(client, _, flags, return_code):
			self.connected = True

		self.mqtt_client.on_connect = _on_connect

		self.mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_TIMEOUT)
		self.mqtt_client.loop_start()

	def _publish(self, weight, unit, mitdatetime, miimpedance):
		if not self.connected:
			raise Exception('not connected to MQTT server')

		check_user = lambda u, w: u['weight_greater_than'] < w < u['weight_lower_than']

		user = next((u for u in USERS if check_user(u, weight)))
		user_name = user['name'] if 'name' in user else 'Unknown'
		message = {
			'Weight': weight
		}
		if user is not None:
			height = user['height']
			age = self.getAge(user['birthdate'])
			sex = user['sex']

			lib = XSBM.bodyMetrics(weight, height, age, sex, miimpedance)
			message['BMI'] =  lib.getBMI()
			message['Basal Metabolism']: lib.getBMR()
			message['Visceral Fat'] = lib.getVisceralFat()

		if mitdatetime:
			message['TimeStamp'] = mitdatetime


		if miimpedance > 0:
			message['Lean Body Mass'] = lib.getLBMCoefficient()
			message['Body Fat'] = lib.getFatPercentage()
			message['Water'] = lib.getWaterPercentage()
			message['Bone Mass'] = lib.getBoneMass()
			message['Muscle Mass'] = lib.getMuscleMass()
			message['Protein'] = lib.getProteinPercentage()


		self.mqtt_client.publish(MQTT_PREFIX + '/' + user_name + '/weight', json.dumps(message), qos=1, retain=True)
		print('\tSent data to topic %s: %s' % (MQTT_PREFIX + '/' + user_name + '/weight', json.dumps(message)))

def main():
	scanner = btle.Scanner().withDelegate(ScanProcessor())
	_ = scanner.scan(5)

if __name__ == '__main__':
	main()
