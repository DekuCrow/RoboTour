#! /usr/bin/python3

import serial
import time
import subprocess

class SensorHub():

	def __init__(self):
		self.baud = 115200
		self.port = self.get_available_port()
		self.serial_port = serial.Serial(port=self.port,\
										 baudrate=self.baud)
		self.n_sonars = 4
		self.sonar_maxrange = 255

		self.tries_limit = 10

		# time to receive response from the hub
		self.response_timeout = 40 #ms
		# time to have the entire frame transmitted
		self.frame_timeout = 20

		self.__DEBUG__ = False


		# the order at which the bytes will come to the sensor
		self.sensors = ['l0', 'l1', 'l2', 'l3', 'l4', 'l5',\
						's0', 's1']
		self.sensor_values = {}

		self.bytes_per_frame = len(self.sensors)

		self.last_poll = 0
		self.last_poll_time = 0

		self.dropped_frames = 0
		self.frame_dropped = False

		self.poll()


	def debug_print(self, message):
		if self.__DEBUG__:
			print(message)

	def get_available_port(self):
		out = subprocess.check_output("ls /dev/ttyACM*", shell=True)
		port = out.split(b'\n')[0].decode('utf-8')
		return port



	def poll(self):
		self.last_poll += 1

		tries = 0
		start = time.perf_counter()


		start = time.perf_counter()

		# discard any outstanding data
		self.serial_port.flushInput()


		while True:
			
			w = self.send_request()
			# see if response received
			if(not w < 0):
				break



		while True:
			
			w = self.send_request()
			# see if response received
			if(not w < 0):
				break
			
			if(tries >= self.tries_limit):
				print("Hub not responsive")
				self.connected = False
				return False
			
			tries += 1

		self.get_frame()
		end = time.perf_counter()
		
		poll_time = (end-start)*1000
		self.debug_print("Response received in {:.2f}ms".format(poll_time))
		self.last_poll_time = poll_time
		self.connected = True
		return True


	def send_request(self):
		
		cycles = 0
		waiting = 0

		dt = 0.001

		self.debug_print("Sending request")

		start = time.perf_counter()
		self.serial_port.write(b'r\n')

		# while no response receieved
		while self.serial_port.inWaiting() < 1:
			# see if we have been waiting for long enough

			if(waiting >= self.response_timeout):
				# self.debug_print(".")
				return -1
			cycles += 1
			time.sleep(dt)
			waiting = (time.perf_counter() - start) * 1000
		
		self.debug_print("Response received after {} cycles ({:.2f}ms)".format(cycles, waiting))
		return waiting



	# THE PROBLEM IS HERE!!!

	# method for receiving the full data frame over serial
	def get_frame(self):

		# for timeout purposes
		waiting = 0
		dt = 0.00001 # 10us
		cycles = 0

		read_wait = 0
		byte_count = 0

		# record starting time
		start = time.perf_counter()
		while True:
			# calculate elapsed time
			waiting = time.perf_counter() - start
			if self.serial_port.inWaiting() > 0:

				read_wait -= time.perf_counter()
				# convert the incoming byte to 
				val = int(self.serial_port.read(1)[0])
				read_wait += time.perf_counter()


		# for timeout purposes
		waiting = 0
		dt = 0.00001 # 10us
		cycles = 0

		read_wait = 0
		byte_count = 0

		# record starting time
		start = time.perf_counter()
		while True:
			# calculate elapsed time
			waiting = time.perf_counter() - start
			if self.serial_port.inWaiting() > 0:

				read_wait -= time.perf_counter()
				# convert the incoming byte to 
				val = int(self.serial_port.read(1)[0])
				read_wait += time.perf_counter()

				self.sensor_values[self.sensors[byte_count]] = val
				byte_count += 1

				if(byte_count == self.bytes_per_frame):
					self.debug_print("Frame received in {} cycles ({:.2f}ms)".format(cycles, waiting*1000))
					self.debug_print("Total read time: {}ms".format(read_wait*1000))
					break
			else:
				# if there is nothing received and we've waited long enough
				if(waiting > self.response_timeout):
					# self.debug_print("!!!Response timeout!!!")
					break
				# wait 10us
				time.sleep(dt)
				cycles += 1

	# THE PROBLEM IS ABOVE !!!

	def extract_from_frame(self, frame):
		if frame is None:
			return
		try:

			# data comes in as 'id0:val0,id1:val1,[...]'
			# split to get identifier-value pairs
			readings = frame.split(',')
			for r in readings:
				#split each pair
				data = r.split(':')
				try:
					self.sensor_values[data[0]] = int(data[1])
				except:
					print("Error with pair: {} : {}".format(data[0], data[1]))
				
				self.debug_print("Sensor {}: {}".format(data[0], data[1]))
			self.frame_dropped = False
		except:
			self.frame_dropped = True
			self.dropped_frames += 1
			print("Error processing frame: {}".format(frame))


class SensorHubFast():

	def __init__(self):
		self.response_timeout = 250/1000
		self.baud = 115200
		self.port = self.get_available_port()
		self.serial_port = serial.Serial(port=self.port,\
										 baudrate=self.baud,
										 timeout=self.response_timeout)
		self.n_sonars = 4
		self.sonar_maxrange = 255

		self.tries_limit = 10

		# time to receive response from the hub
		# time to have the entire frame transmitted
		self.frame_timeout = 20

		self.__DEBUG__ = False


		# the order at which the bytes will come to the sensor
		self.sensors = ['l0', 'l1', 'l2', 'l3', 'l4', 'l5',\
						's0', 's1']
		self.sensor_values = {}

		self.bytes_per_frame = len(self.sensors)

		self.last_poll = 0
		self.last_poll_time = 0

		self.poll()


	def debug_print(self, message):
		if self.__DEBUG__:
			print(message)

	def get_available_port(self):
		out = subprocess.check_output("ls /dev/ttyACM*", shell=True)
		port = out.split(b'\n')[0].decode('utf-8')
		return port



	def poll(self):
		self.last_poll += 1

		tries = 0
		start = time.perf_counter()

		# discard any outstanding data
		self.serial_port.flushInput()


		while True:
			
			w = self.send_request()
			# see if response received
			if(not w < 0):
				break
			
			if(tries >= self.tries_limit):
				print("Hub not responsive")
				self.connected = False
				return False
			
			tries += 1

		self.get_frame()
		end = time.perf_counter()
		
		poll_time = (end-start)*1000
		self.last_poll_time = poll_time
		self.connected = True
		return True

	def send_request(self):
		
		waiting = 0

		dt = 0.001

		start = time.perf_counter()
		self.serial_port.write(b'r\n')

		# while no response receieved
		while self.serial_port.inWaiting() < 1:
			# see if we have been waiting for long enough

			if(waiting >= self.response_timeout):
				# self.debug_print(".")
				return -1
			time.sleep(dt)
			waiting = (time.perf_counter() - start) * 1000
		
		return waiting



	# THE PROBLEM IS HERE!!!

	# method for receiving the full data frame over serial
	def get_frame(self):

		byte_count = 0
		vals = self.serial_port.read(self.bytes_per_frame)

		for v in vals:
			self.sensor_values[self.sensors[byte_count]] = int(v)
			byte_count += 1

		if(byte_count < self.bytes_per_frame):
			print("PROBELEM")

		

class HubSonar():

	def __init__(self, hub, name):
		self.hub = hub
		self.hub_key = name
		self.last_poll = -1
		self.maxrange = self.hub.sonar_maxrange

		self.hub.sensor_values[name] = 0
		self.val = 0

	def value(self):
		# if a new value is requested
		if self.last_poll == self.hub.last_poll:
			self.hub.poll()

		self.last_poll = self.hub.last_poll
		self.val = self.hub.sensor_values[self.hub_key]
		self.val = self.maxrange if self.val == 0 else self.val
		return self.val

class HubLineSensor():
	def __init__(self, hub):
		self.num_sensors = 6
		self.sensor_names = ["l{}".format(i) for i in range(self.num_sensors)]

		self.hub = hub

		self.last_poll = -1

		self.raw_val = {}
		self.prev_val = {}
		# intialise the sensor readings
		for n in self.sensor_names:
			self.hub.sensor_values[n] = 0


	def raw_values(self):

		# if a new value is requiested
		if self.last_poll == self.hub.last_poll:
			self.hub.poll()

		self.last_poll = self.hub.last_poll
		for n in self.sensor_names:
			self.raw_val[n] = self.hub.sensor_values[n]

		return self.raw_val 

	def value_simple(self):

		self.raw_values()
		order = ['l0', 'l1', 'l2', 'l3', 'l4', 'l5']

		weight = 10
		floor = 235
		line = 185
		threshold = (floor+line)/2

		err = 0
		activated_sens = 0

		for s in order:

			val = self.raw_val[s]


			#check if sensor on line
			if val < threshold:
				err += weight
				activated_sens += 1

			weight += 10

		if activated_sens > 0:
			return err/activated_sens
		else:
			return 0 


if __name__ == "__main__":
	sh = SensorHub()
	while True:
		sh.poll()