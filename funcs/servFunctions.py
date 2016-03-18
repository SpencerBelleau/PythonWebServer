def wrapString(string):
	return "\"" + string + "\""
def parseRequest(request):
	#First, split the request into its logical parts
	lines = request.split('\r\n')
	#next, split the first piece into COMMAND, PATH, VER
	cpv = lines[0].split(' ')
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
			getData = lines[11]
			getData = getData.replace("&", " ")
		except:
			path = cpv[1]
			getData = ""
	return (cpv[0], path, getData)
def indexLink(str):
	if("." in str[1:]):
		return str
	else:
		return (str + "/")