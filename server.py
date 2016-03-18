from socket import socket, AF_INET, SOCK_STREAM
import os, subprocess
listen = socket(AF_INET, SOCK_STREAM)
listen.bind(('', 80))
listen.listen(5)
root = os.path.abspath(os.path.dirname(__file__))
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
#print(root)
while True:
	con, addr = listen.accept()
	try:
		rawRequest = con.recv(2048).decode()
		#print(rawRequest)
		type, req, getData = parseRequest(rawRequest)
		#print(req)
		#print(getData)
		print("New " + type + " request from " + str(addr) + " for " + str(req))
		if(req == "/"):
			res = open('html/index.html', 'rb')
			con.send(res.read())
		else:
			if(req[-4:] == ".php"):
				try:
					res = subprocess.getoutput("php-cgi -f " + wrapString(root + req) + " " + getData)
				except Exception as e:
					print(e)
					res = "N/A".encode()
				con.send(res.encode())
			elif(req[-3:] == ".py"):
				try:
					res = subprocess.getoutput("py " + wrapString(root + req) + " " + getData)
				except Exception as e:
					print(e)
					res = "N/A".encode()
				con.send(res.encode())
			else:
				try:
					res = open(root + req, 'rb')
					con.send(res.read())
				except:
					print("Bad request: " + str(req))
					con.send("<h1 style='text-align:center'>404 lol</h1>".encode())
					con.send("<a style='text-align:center' href='/'>Back to Index</a>".encode())
		print("--------------")
	except Exception as e:
		msg = "An error has occurred: " + str(e)
		con.send(msg.encode())
	#con.send('HTTP/1.1 200 OK\r\n\r\n<h1>Hi</h1>'.encode())
	con.close()