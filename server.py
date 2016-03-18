from socket import socket, AF_INET, SOCK_STREAM
import os, subprocess
listen = socket(AF_INET, SOCK_STREAM)
listen.bind(('', 80))
listen.listen(5)
root = os.path.abspath(os.path.dirname(__file__))
def wrapString(string):
	return "\"" + string + "\""

print(root)
while True:
	con, addr = listen.accept()
	try:
		rawRequest = con.recv(2048).decode()
		list = rawRequest.split(" ")
		req = list[1]
		print("New request from " + str(addr) + " for " + str(req))
		if(req == "/"):
			res = open('html/index.html', 'rb')
			con.send(res.read())
		else:
			if(req[-4:] == ".php"):
				try:
					res = subprocess.getoutput("php " + wrapString(root + req))
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
				
	except Exception as e:
		msg = "An error has occurred: " + str(e)
		con.send(msg.encode())
	#con.send('HTTP/1.1 200 OK\r\n\r\n<h1>Hi</h1>'.encode())
	con.close()