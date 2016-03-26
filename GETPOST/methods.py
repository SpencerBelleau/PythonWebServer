import sys, collections, urllib.parse
##TAKES IN ENTIRE REQUEST INCLUDING HEADER
##ALWAYS PUT IT IN A TRY
def parsePost(raw):
	ret = []
	head, raw = raw.split(b'\r\n\r\n', 1)
	#Ajax is a pain in the ass
	head = head.split(b'\r\n')
	for field in head:
		field = field.split(b' ')
		if(field[0] == b'Content-Type:'):
			type = field[1]
			if(type == b'application/x-www-form-urlencoded;'):
				#This is an AJAX submission
				raw = raw.split(b'&')
				for pair in raw:
					pair = pair.split(b'=')
					ret.append(('formData', b'"' + pair[0] + b'"', pair[1]))
				return ret
			else:
				break #Not AJAX
	#End dumb Ajax code
	boundary, raw = raw.split(b'\r\n', 1)
	#print(boundary)
	parts = raw.split(b'\r\n' + boundary)
	for part in parts:
		try:
			head, data = part.split(b'\r\n\r\n', 1) #split local headers off
			head = head.split(b'\r\n') #separate the fields
			for field in head:
				field = field.split(b' ')
				if(field[0] == b"Content-Disposition:"):
					#print("Getting Filename")
					try:
						filename = field[3].split(b"=")[1]
						ret.append(('file', filename, data))
					except: #Normally this isn't required at all, since checking the data type will determine if it's form data
						name = field[2].split(b"=")[1]
						ret.append(('formData', name, data))
		except:
			pass
	return ret
##OUTPUTS LIST OF TUPLES ('type', 'field/filename', data)

##TAKES NO ARGUMENTS, READS sys.argv
def parseGetData():
	if(len(sys.argv) > 1):
		gets = sys.argv[1].split(" ")
		#print(gets)
		keyVals = collections.OrderedDict()
		for i in range(len(gets)):
			try:
				key, val = gets[i].split("=", 1)
				key = urllib.parse.unquote_plus(key)
				val = urllib.parse.unquote(val)
				keyVals[key] = val
				#print(key)
				#print(val)
			except Exception as e:
				#print(e)
				#print("Error, bad keyval: " + gets[i])
				key = gets[i][-1:]
				val = ""
		return keyVals
	return {}
##OUTPUTS DICT OF PARAMETERS IN FORM {fieldname, value}