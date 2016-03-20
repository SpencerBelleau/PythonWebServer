from socket import socket, AF_INET, SOCK_STREAM
import os, subprocess, sys, urllib.request, urllib.parse, threading, json
from funcs.servFunctions import *
listen = socket(AF_INET, SOCK_STREAM)
listen.bind(('', 80))
listen.listen(5)
root = os.path.abspath(os.path.dirname(__file__))
def thread(con, addr):
	con.settimeout(10)
	persistent = True
	while persistent:
		try:
			rawRequest = con.recv(2048).decode()
		except:
			print("Closing port " + str(addr[1]))
			break
		try:
			type, req, getData, persistent = parseRequest(rawRequest)
			print(str(addr) + ": " + type + " " + str(req))
			header = "HTTP/1.1 200 OK\r\n"
			if(persistent):
				header += "Connection: keep-alive\r\n"
			else:
				header += "Connection: close\r\n"
			req = escapeQuotes(req)
			req = urllib.parse.unquote_plus(req)
			getData = urllib.parse.unquote_plus(getData)
			if(req[-1] == "/"):
				try:
					res = open(root + req + 'index.html', 'rb')
					resp = res.read()
					res.close()
				except:
					try:
						t = open(root + req + "index.php", 'rb')
						t.close()
						resp = subprocess.getoutput("php-cgi -f " + wrapString(root + req + "index.php") + " " + getData).encode()
					except:
						try:
							t = open(root + req + "index.py", 'rb')
							t.close()
							resp = subprocess.getoutput("py " + wrapString(root + req + "index.py") + " " + getData).encode()
						except:
							resp = ""
							resp += "<!DOCTYPE html><html><h2>Index of " + req + "</h2><ul><li><a href='..'>..</a></li>"
							for name in (os.listdir(root + req)):
								if(name == sys.argv[0].split('\\')[-1]):
									continue
								else:
									resp += "<li><a href='" + indexLink(urllib.parse.quote_plus(name), (root + req)) + "'>" + indexLink(name, (root + req)) + "</a></li>"
							resp += "</ul></html>"
							resp = resp.encode()
			else:
				if(req[-4:] == ".php"):
					try:
						resp = subprocess.getoutput("php-cgi -f " + wrapString(root + req) + " " + getData).encode()
					except Exception as e:
						print(e)
						resp = "N/A".encode()
				elif(req[-3:] == ".py"):
					try:
						resp = subprocess.getoutput("py " + wrapString(root + req) + " " + getData).encode()
					except Exception as e:
						print(e)
						resp = "N/A".encode()
				else:
					try:
						res = open(root + req, 'rb')
						resp = res.read()
						res.close()
					except:
						print("Bad request: " + str(req))
						resp = "<h1 style='text-align:center'>404 lol</h1><a style='text-align:center' href='/'>Back to Index</a>".encode()
		except Exception as e:
			header = "HTTP/1.1 200 OK\r\n"
			header += "Connection: close\r\n"
			resp = ("An error has occurred: " + str(e)).encode()
		length = len(resp)
		header += "content-length: " + str(length) + "\r\n"
		header += "\r\n"
		con.send(header.encode())
		con.send(resp)
	con.close()
try:
	myIP = json.loads(urllib.request.urlopen("https://api.ipify.org/?format=json").read().decode())["ip"]
	print("Server hosted @ " + myIP + ":80")
	while True:
		con, addr = listen.accept()
		threading.Thread(target=thread, args=(con, addr)).start()
except:
	print("No internet connection.")