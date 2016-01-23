import socket
import sys
from thread import *

HOST = ''
PORT = 8888
BACKLOG = 10
RECV_BUFLEN = 4096

def print_error(name, msg):
	print name + ' failed.'
	print 'error code: ' + str(msg[0])
	print  'description: ' + str(msg[1])

def client_handler(conn, host_name, port):

	print 'client: '+ str(host_name) + ':' + str(port)
	
	while True:
		try:
			data = conn.recv(RECV_BUFLEN)
		except socket.error as msg:
			print_error("recv", msg)
			conn.close()
			return

		reply = data

		if not data:
			break

		#echo server
		conn.sendall(reply)

	conn.close()
	print 'client ' + str(host_name) + ':' + str(port) + ' done'

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
	print_error("socket", msg)
	sys.exit()

try:
	s.bind((HOST, PORT))
except socket.error as msg:
	print_error("bind", msg)
	sys.exit()

s.listen(BACKLOG)
print 'Listening...'

while True:
	try:
		conn, addr = s.accept()
	except KeyboardInterrupt:
		print 'exiting...'
		s.close()
		sys.exit()
	except Exception,e:
		print 'accept failed.'
		print 'exception: ' + str(e)
		s.close()
		sys.exit()

	start_new_thread(client_handler, (conn,addr[0], addr[1],))

s.close()
