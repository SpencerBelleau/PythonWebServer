from socket import socket, AF_INET, SOCK_STREAM
import os, subprocess, sys, urllib.request, urllib.parse, threading, json
from funcs.servFunctions import *
listen = socket(AF_INET, SOCK_STREAM)
listen.bind(('', 80))
listen.listen(5)
root = os.path.abspath(os.path.dirname(__file__))
#print(root)
def thread(con, addr):
	try:
		rawRequest = con.recv(2048).decode()
		#print(rawRequest)
		type, req, getData = parseRequest(rawRequest)
		#print(req)
		#print(getData)
		print(str(addr) + ": " + type + " " + str(req))
		header = "HTTP/1.1 200 OK\r\n\r\n"
		con.send(header.encode())
		req = urllib.parse.unquote_plus(req)
		if(req[-1] == "/"):
			try:
				#print("Trying HTML")
				res = open(root + req + 'index.html', 'rb')
				con.send(res.read())
				res.close()
			except:
				try:
					#print("Trying PHP")
					#req = "/php/index.php"
					t = open(root + req + "index.php", 'rb')
					res = subprocess.getoutput("php-cgi -f " + wrapString(root + req + "index.php") + " " + getData)
					#res = open('php/index.php', 'rb')
					con.send(res.encode())
					t.close()
				except:
					try:
						#print("Trying Python")
						#req = "/python/index.py"
						t = open(root + req + "index.py", 'rb')
						res = subprocess.getoutput("py " + wrapString(root + req + "index.py") + " " + getData)
						#res = open('python/index.py')
						con.send(res.encode())
						t.close()
					except:
						res = ""
						res += "<!DOCTYPE html><html><h2>Index of " + req + "</h2><ul><li><a href='..'>..</a></li>"
						for name in (os.listdir(root + req)):
							if(name == sys.argv[0].split('\\')[-1]):
								continue
							else:
								res += "<li><a href='" + indexLink(name, (root + req)) + "'>" + indexLink(name, (root + req)) + "</a></li>"
						res += "</ul></html>"
						con.send(res.encode())
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
					res.close()
				except:
					print("Bad request: " + str(req))
					con.send("<h1 style='text-align:center'>404 lol</h1>".encode())
					con.send("<a style='text-align:center' href='/'>Back to Index</a>".encode())
	except Exception as e:
		res = "An error has occurred: " + str(e)
		con.send(res.encode())
	con.close()
try:
	myIP = json.loads(urllib.request.urlopen("http://ip.jsontest.com/").read().decode())["ip"]
	print("Server hosted @ " + myIP + ":80")
	while True:
		con, addr = listen.accept()
		threading.Thread(target=thread, args=(con, addr)).start()
except:
	print("No internet connection.")