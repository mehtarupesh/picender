import socket
import sys
import time
from metadata import *
from thread import *
import ntpath

HOST = ''
PORT = 8888
BACKLOG = 10
RECV_BUFLEN = 4096
DATA_BUFLEN = (16 * 4096)
STORAGE_DIR_PATH = os.getcwd()+"/storage"

def print_error(name, msg):
	print name + ' failed.'
	print 'error code: ' + str(msg[0])
	print  'description: ' + str(msg[1])


def gen_fname(fdir, fid):
	head, tail = ntpath.split(fid)

	fdir_abs_path = STORAGE_DIR_PATH + '/' + fdir

	if not os.path.exists(fdir_abs_path):
		os.makedirs(fdir_abs_path)

	return fdir_abs_path+'/'+tail

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

	print 'fdir   = ' + get_fdir(fheader)
	print 'fid   = ' + get_fid(fheader)
	print 'fsize = ' + str(get_fsize(fheader))

	recd_fname = gen_fname(get_fdir(fheader), get_fid(fheader))

	try:
		fobj = open(recd_fname,'wb')
	except Exception, e:
		print 'open file failed'
		print 'Exception : ' + str(e)
		conn.close()
		return

	recd_bytes = 0
	start_ts = time.time()
	# get file contents
	while True:
		try:
			data = conn.recv(DATA_BUFLEN)
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
		#conn.sendall(reply)

	end_ts = time.time()
	fobj.close()
	conn.close()

	if recd_bytes != get_fsize(fheader):
		print 'Error in num of bytes received: '
		print 'Expected : ' + str(get_fsize(fheader)) + ' bytes'
		print 'Received : ' + str(recd_bytes) + ' bytes'
		os.remove(recd_fname)
	else:		
		print 'Successfully recd: ' + str(recd_bytes) + ' bytes : [' + str(recd_bytes/(end_ts - start_ts)) + '] bytes per second'

	print time.strftime("%c")
	print '----------------------------------------------------------'

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
