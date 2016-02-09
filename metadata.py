import hmac
from hashlib import sha1
import os
import pickle
import json

SHARED_KEY = 'cigital/ds/12@33!'
DELIMITER = '@@##$$^^'
HEADER_SIZE = 512
ID_STRING = 'ID'
LEN_STRING = 'LENGTH'

# return tuple of id, size
def gen_prop(fname):
	fid   = os.path.abspath(fname)
	finfo = os.stat(fname)
	fsize = finfo.st_size
	fprop = (fid, fsize)
	return fprop

#formatting functions
def gen_header_string(fprop):
	#Method 1: pickle
	#return pickle.dumps(fprop)

	#Method 2: Json
	flist = {}
	flist[ID_STRING] = str(fprop[0])
	flist[LEN_STRING] = str(fprop[1])
	return json.dumps(flist)

def gen_header_obj(hstr):
	#Method 1: pickle
	#return pickle.loads(hstr)

	#Method 2: Json
	flist = json.loads(hstr)
	fprop = (flist[ID_STRING], int(flist[LEN_STRING]))

	return fprop

def crpyt(fprop):
	fheader = gen_header_string(fprop)
	fdigest = hmac.new(SHARED_KEY, fheader, sha1).hexdigest()
 
	fsendheader = DELIMITER + str(fdigest) + DELIMITER + str(fheader)

	if HEADER_SIZE < len(fsendheader):
		print '****** header exceeding size limit!!'
		return None

	padding = "X" * (HEADER_SIZE - len(fsendheader))
	fsendheader = padding + fsendheader

	#print 'Sending...' + str(fsendheader)
	#print ' length ' + str(len(fsendheader)) + ' bytes'
	return fsendheader

def decrypt(data):

	try:

		if len(data) != HEADER_SIZE:
			print '****** LENGTH != HEADER_SIZE'
			return None

		#print 'Received : '+ str(data)
		padding, recd_fdigest, recd_fheader = data.split(DELIMITER)
	except Exception,e:
		print '****** decrpyt: split failure: DELIMITER = '+DELIMITER
		print '****** split = '+ str(data.split(DELIMITER))
		return None

	new_fdigest = str(hmac.new(SHARED_KEY, recd_fheader, sha1).hexdigest())

	# python >= 2.7.7 has compare_digest
	#if hmac.compare_digest(recd_fdigeststr, new_fdigest) == false:
	if recd_fdigest != new_fdigest:
		print '****** authentication error:'
		print '****** recvd digest = ' + str(recd_fdigest)
		print '****** generated digest = ' + str(new_fdigest)
		return None

	fprop_recd = gen_header_obj(recd_fheader)
	return fprop_recd