#!/usr/bin/python
import time
import socket
import struct
import decimal
import multiprocessing
import sys
import datetime

FORMAT = ">BBBBII4sQQQQ"

def someHelp():
	print("This is fake SNTP server")
	print("Call it with digit argument, which will be interpreted as shift in seconds")

class SockProcess(multiprocessing.Process):
	def __init__(self, data, addr, s, shift, receive_time):
		self.data = data
		self.addr = addr
		self.s = s
		self.shift = shift
		self.receive_time = receive_time
		multiprocessing.Process.__init__(self)
	def run(self):
		request = struct.unpack(FORMAT, self.data)
		transmit_time = to_ntp(time.time())
		originate_time = request[-1]
		ntp_shift = (decimal.Decimal(self.shift)) * (2 ** 32)
		send_data = struct.pack(FORMAT, 36, 2, 0, 0, 0, 0, b'', 0, int(originate_time),
			int(self.receive_time + ntp_shift), int(transmit_time + ntp_shift))
		self.s.sendto(send_data, self.addr)

def to_ntp(time):
	return int((decimal.Decimal(time + 2208988800)) * (2 ** 32)) # time in secs since 1900, 32 for int and 32 for part

def main(shift):
	shift = float(shift)
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname('udp'))
	s.bind(("", 123))

	while 1:
		data, addr = s.recvfrom(1024)
		receive_time = to_ntp(time.time())
		SockProcess(data, addr, s, shift, receive_time).start()
	s.close()


if __name__ == "__main__":
	if len(sys.argv) == 1:
		someHelp()
		sys.exit()
	else:
		main(sys.argv[1])