from socket import socket, AF_INET, SOCK_STREAM
import os, subprocess, sys, urllib.request, urllib.parse, threading, json
from funcs.servFunctions import *
try:
	config = json.loads(open("config.json", 'r').read())
except:
	print("Error loading config")
	sys.exit(-1)
listen = socket(AF_INET, SOCK_STREAM)
listen.bind(('', 80))
listen.listen(5)
root = os.path.abspath(os.path.dirname(__file__))
def thread(con, addr):
	if(config["persistent"]):
		con.settimeout(config["timeout"])
	persistent = True
	while persistent:
		#First, try to get data
		try:
			byteRequest = con.recv(config["buffersize"])
			rawRequest = byteRequest.decode()
		except:
			print("Closing port " + str(addr[1]))
			break
		#Then, try to respond
		try:
			#Parse useful information out of the HTTP header
			type, req, getData, persistent = parseRequest(rawRequest)
			#Print a log
			print(str(addr) + ": " + type + " " + str(req))
			#Initialize the header, this may get changed later
			header = "HTTP/1.1 200 OK\r\n"
			#If we've configured ourselves for persistent connections, use persistent mode
			if(persistent and config["persistent"]):
				header += "Connection: keep-alive\r\n"
			else:
				header += "Connection: close\r\n"
				persistent = False
			#Remove any HTTP formatting from the request
			req = escapeQuotes(req)
			req = urllib.parse.unquote_plus(req)
			getData = urllib.parse.unquote_plus(getData)
			#If we're redirecting, do it
			if(req == "/" and config["redirectRoot"]["on"]):
				header = "HTTP/1.1 302 Found\r\n"
				header += "Location: /" + config["redirectRoot"]["location"] + "\r\n"
				resp = ""
			#Else, if no file is specified
			elif(req[-1] == "/"):
				#Look for index files
				header = "HTTP/1.1 302 Found\r\n"
				if(os.path.isfile(root + req + 'index.html')):
					header += "Location: " + req + "index.html\r\n"
					resp = ""
				elif(os.path.isfile(root + req + 'index.php')):
					header += "Location: " + req + "index.php\r\n"
					resp = ""
				elif(os.path.isfile(root + req + 'index.py')):
					header += "Location: " + req + "index.py\r\n"
					resp = ""
				else:
					#If there are no index files, generate one
					resp = "<!DOCTYPE html><html><head><title>Index of " + req + "</title></head><body><h2>Index of " + req + "</h2><ul><li><a href='..'>..</a></li>"
					for name in (os.listdir(root + req)):
						if(name == sys.argv[0].split('\\')[-1]):
							continue
						else:
							resp += "<li><a href='" + indexLink(urllib.parse.quote_plus(name), (root + req)) + "'>" + indexLink(name, (root + req)) + "</a></li>"
					resp += "</ul></body></html>"
					resp = resp.encode()
			#else, if a file is specified
			else:
				#See if our file exists, if it does then...
				if(os.path.isfile(root + req)):
					#Try to run it
					if(req[-4:] == ".php"):
						try:
							resp = subprocess.getoutput("php-cgi -f " + wrapString(root + req) + " " + getData).encode()
						except Exception as e:
							print(e)
							resp = "could not run PHP script".encode()
					elif(req[-3:] == ".py"):
						try:
							#resp = subprocess.getoutput("py " + wrapString(root + req) + " " + getData).encode()
							resp = subprocess.Popen([sys.executable, root + req, getData], stdout=subprocess.PIPE, cwd=(os.path.split(root+req)[0])).communicate()[0] #UGLY, but it works
						except Exception as e:
							print(e)
							resp = "could not run Python script".encode()
					#If it's not a runnable, read it
					else:
						try:
							res = open(root + req, 'rb')
							resp = res.read()
							res.close()
						#If we can't read it we've screwed up
						except Exception as e:
							print(e)
							header = "HTTP/1.1 500 Internal Server Error\r\n"
							header += "Connection: close\r\n"
							resp = ("An error has occurred: " + str(e)).encode()
				#If the file doesn't exist, give a 404
				else:
					print("Bad request: " + str(req))
					header = "HTTP/1.1 404 Not Found\r\n"
					resp = "<h1 style='text-align:center'>404 lol</h1><a style='text-align:center' href='/'>Back to Index</a>".encode()
		#If at any point we crash, send a 500
		except Exception as e:
			print(e)
			print("Internal Server Error")
			header = "HTTP/1.1 500 Internal Server Error\r\n"
			header += "Connection: close\r\n"
			resp = ("An error has occurred: " + str(e)).encode()
		#Get the content length
		length = len(resp)
		#Append the header
		header += "content-length: " + str(length) + "\r\n"
		header += "\r\n"
		#Try to send
		try:
			con.send(header.encode())
			#If there's actual content, send that too
			if(length > 0):
				con.send(resp)
		#If the socket is closed, say so
		except Exception as e:
			print(e)
			print("Send error: socket " + str(addr[1]) + " closed by client")
			break
	#Close when we're done
	con.close()
try:
	myIP = json.loads(urllib.request.urlopen("https://api.ipify.org/?format=json").read().decode())["ip"]
	print("Server hosted @ " + myIP + ":80")
	while True:
		con, addr = listen.accept()
		threading.Thread(target=thread, args=(con, addr)).start()
except:
	print("No internet connection.")