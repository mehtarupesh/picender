import socket
import sys, getopt

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

chunk = fobj.read(RECV_BUFLEN)
while chunk:
	print 'reading..sending ' + str(len(chunk)) + ' bytes' 
	print str(chunk)

	try:
		s.sendall(chunk)
	except Exception, e:
		print 'sending failed...'
		print 'Exception:' + str(e)
		fobj.close()
		s.close()
		sys.exit()

	recv_str = s.recv(RECV_BUFLEN)
	print 'received... ' + str(len(recv_str)) + ' bytes'

	if chunk != recv_str:
		print 'invalid loopback'
		print 'sent : ' + str(chunk)
		print 'recvd : ' + str(recv_str)
		fobj.close()
		s.close()
		sys.exit()

	chunk = fobj.read(RECV_BUFLEN)

print 'done...'
fobj.close()
s.close()
	