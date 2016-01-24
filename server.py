import socket
import sys
from metadata import *
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

	#get file mehta data
	try:
		data = conn.recv(HEADER_SIZE)
	except socket.error as msg:
		print_error("recv", msg)
		conn.close()
		return

	fheader = decrypt(data)
	if fheader == None:
		conn.close()
		return

	print 'fid   = ' + str(fheader[0])
	print 'fsize = ' + str(fheader[1])

	recd_bytes = 0
	recd_fname = str(fheader[0])+'.recd'

	try:
		fobj = open(recd_fname,'wb')
	except Exception, e:
		print 'open file failed'
		print 'Exception : ' + str(e)
		conn.close()
		return

	# get file contents
	while True:
		try:
			data = conn.recv(RECV_BUFLEN)
		except socket.error as msg:
			print_error("recv", msg)
			fobj.close()
			os.remove(recd_fname)
			conn.close()
			return

		if not data:
			break

		recd_bytes += len(data)
		reply = data
		fobj.write(data)

		#echo server
		conn.sendall(reply)

	fobj.close()
	conn.close()

	if recd_bytes != fheader[1]:
		print 'Error in num of bytes received: '
		print 'Expected : ' + str(fheader[1]) + ' bytes'
		print 'Received : ' + str(recd_bytes) + ' bytes'
		os.remove(recd_fname)
	else:		
		print 'Successfully recd: '

	print 'From client ' + str(host_name) + ':' + str(port) + ' done'

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
