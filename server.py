import socket
import pickle
import sys
from thread import *
import hmac
from hashlib import sha1

HOST = ''
PORT = 8888
BACKLOG = 10
RECV_BUFLEN = 4096
SHARED_KEY = 'cigital/ds/12@33!'

def print_error(name, msg):
	print name + ' failed.'
	print 'error code: ' + str(msg[0])
	print  'description: ' + str(msg[1])

def crpyt(fprop):
	fheader = pickle.dumps(fprop)
	fdigest = hmac.new(SHARED_KEY, fheader, sha1).hexdigest()
 
	fsendheader = fdigest + ' ' + fheader
	return fsendheader

def decrypt(data):
	recd_fdigest, recd_fheader = data.split(' ')
	new_fdigest = hmac.new(SHARED_KEY, recd_fheader, sha1).hexdigest()

	# python >= 2.7.7 has compare_digest
	#if hmac.compare_digest(recd_fdigeststr, new_fdigest) == false:
	if recd_fdigest != new_fdigest:
		print 'authentication error:'
		print 'recvd digest = ' + str(recd_fdigest)
		print 'generated digest = ' + str(new_fdigest)
		return None

	fprop_recd = pickle.loads(recd_fheader)
	return fprop_recd

def client_handler(conn, host_name, port):

	print 'client: '+ str(host_name) + ':' + str(port)

	#get file mehta data
	try:
		data = conn.recv(RECV_BUFLEN)
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
	# get file contents
	while True:
		try:
			data = conn.recv(RECV_BUFLEN)
		except socket.error as msg:
			print_error("recv", msg)
			conn.close()
			return

		recd_bytes += len(data)
		reply = data

		if not data:
			break

		#echo server
		conn.sendall(reply)

	conn.close()

	if recd_bytes != fheader[1]:
		print 'Error in num of bytes received: '
		print 'Expected : ' + str(fheader[1]) + ' bytes'
		print 'Received : ' + str(recd_bytes) + ' bytes'
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
