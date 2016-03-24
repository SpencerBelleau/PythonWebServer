import os, urllib.parse
def wrapString(string):
	return "\"" + string + "\""
def parseRequest(request):
	#First, split the request into its logical parts
	lines = request.split('\r\n')
	for i in range(len(lines)):
		lines[i] = lines[i].split(" ")
	#next, split the first piece into COMMAND, PATH, VER
	cpv = lines[0]
	#also, check if we need to keep-alive
	#print(getParsedArgs(lines, "Connection:"))
	try:
		if(getParsedArgs(lines, "Connection:")[1] == "keep-alive"):
			persistent = True
		else:
			persistent = False
	except:
		print("No connection field in request.")
		print(request)
		persistent = False
	#print(cpv)
	#If it's a GET
	if(cpv[0] == "GET"):
		#Split off the GET data, if there is any.
		try:
			path, getData = cpv[1].split("?")
			#replace all the ampersands
			getData = getData.replace("&", " ")
		except:
			path = cpv[1]
			getData = ""
	else:
		#POST is not supported
		#Data is parsed and treated as GET
		try:
			path = cpv[1]
			getData = lines[len(lines)-1]
			getData = getData.replace("&", " ")
		except:
			path = cpv[1]
			getData = ""
	return (cpv[0], path, getData, persistent)
def readReqBeta(request):
	#First, split the request into its logical parts
	lines = request.split('\r\n')
	for i in range(len(lines)):
		lines[i] = lines[i].split(" ")
	print(getParsedArgs(lines, "Connection:"))
def getParsedArgs(reqList, field):
	for x in reqList:
		if(x[0] == field):
			return x
	return []
def escapeQuotes(str):
	ret = ""
	for char in str:
		if(char == "\'"):
			ret += "\\"
			ret += char
		elif(char == "\""):
			ret += "\\"
			ret += char
		else:
			ret += char
	return ret
def indexLink(str, path):
	loc = urllib.parse.unquote_plus(path + str)
	if(os.path.isfile(loc)):
		return str
	else:
		return (str + "/")
def isRedirect(config, request):
	urls = config["redirects"]["urls"]
	if((request in urls) and config["redirects"]["on"]):
		return True
	else:
		return False
def redirect(config, request):
	urls = config["redirects"]["urls"]
	try:
		return urls[request]
	except:
		return request