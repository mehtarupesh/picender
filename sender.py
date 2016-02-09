import socket
import sys, getopt, os
from metadata import *

SERVER = 'localhost'
PORT = 8888
RECV_BUFLEN = 4096

def print_error(name, msg):
	print name + ' failed.'
	print 'error code: ' + str(msg[0])
	print  'description: ' + str(msg[1])

def usage():
	print 'usage: sender.py -f <file>'

def parse_args(argv):
	in_file = ''
	try:
		opts, args = getopt.getopt(argv, "h:f:", ["--help", "ifile="])
	except getopt.GetoptError:
		usage()
		sys.exit()
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print 'sender.py -f <file>'
			sys.exit()
		elif opt in ("-f", "--ifile"):
			in_file = arg

	return in_file

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
	print_error("socket")
	sys.exit()

try:
	remote_ip = socket.gethostbyname(SERVER)
except socket.gaierror,e:
	print "gaierror for host: " + SERVER
	print "error: " + str(e)
	sys.exit()

try:
	s.connect((remote_ip, PORT))
except Exception,e:
	print "error connecting to: " + str(remote_ip) + ':' + str(PORT)
	print "exception: " + str(e)
	sys.exit()

print 'connected to ' + str(remote_ip) +':'+str(PORT)

fname = parse_args(sys.argv[1:])
if fname == '':
	print 'Please specify file'
	usage()
	sys.exit(0)

try:
	fobj = open(fname, 'rb')
except Exception, e:
	print 'open file failed'
	print 'Exception : ' + str(e)
	s.close()
	sys.exit()


fprop = gen_prop(fname)
print 'fdir   = ' + get_fdir(fprop)
print 'fid   = ' + get_fid(fprop)
print 'fsize = ' + str(get_fsize(fprop))

#send file mehta data
fsendheader = crpyt(fprop)	

if fsendheader == None:
	fobj.close()
	s.close()
	sys.exit()

try:
	sent = 0
	while sent < len(fsendheader):
		sent += s.send(fsendheader[sent:])

except Exception, e:
	print 'sending failed...'
	print 'Exception:' + str(e)
	fobj.close()
	s.close()
	sys.exit()

#send file contents
chunk = fobj.read(RECV_BUFLEN)
sent_bytes = 0
while chunk:
	try:
		s.sendall(chunk)
	except Exception, e:
		print 'sending failed...'
		print 'Exception:' + str(e)
		fobj.close()
		s.close()
		sys.exit()

	sent_bytes += len(chunk)

	# recv echo from server
	# recv_str = s.recv(RECV_BUFLEN)
	# if chunk != recv_str:
	# 	print '****** invalid loopback'
	# 	print '****** sent : ' + str(chunk)
	# 	print '****** recvd : ' + str(recv_str)
	# 	fobj.close()
	# 	s.close()
	# 	sys.exit()

	chunk = fobj.read(RECV_BUFLEN)

if sent_bytes != get_fsize(fprop):
	print '****** Error : sent_bytes != file_size'
else:
	print 'DONE...'
fobj.close()
s.close()
	