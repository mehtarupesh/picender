import socket
import pickle
import sys, getopt, os
import hmac
from hashlib import sha1

SERVER = 'localhost'
PORT = 8888
RECV_BUFLEN = 4096
SHARED_KEY = 'cigital/ds/12@33!'

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

# return tuple of id, size
def gen_prop(fname):
	fid   = os.path.abspath(fname)
	finfo = os.stat(fname)
	fsize = finfo.st_size
	fprop = (fid, fsize)
	return fprop

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
		fobj.close()
	 	s.close()
	 	sys.exit()

	fprop_recd = pickle.loads(recd_fheader)
	return fprop_recd


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
print 'id : ' + str(fprop[0])
print 'size : ' + str(fprop[1])

#send file mehta data
fsendheader = crpyt(fprop)	
try:
	s.sendall(fsendheader)
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
	recv_str = s.recv(RECV_BUFLEN)

	if chunk != recv_str:
		print 'invalid loopback'
		print 'sent : ' + str(chunk)
		print 'recvd : ' + str(recv_str)
		fobj.close()
		s.close()
		sys.exit()

	chunk = fobj.read(RECV_BUFLEN)

if sent_bytes != fprop[1]:
	print '***Error : sent_bytes != file_size'
else:
	print 'done...'
fobj.close()
s.close()
	