import os
import time
import sys
import socket
import select

c_title={}
k=-1
c_data={}
c_time={}
c_count={}

HOST = ""
PORT = 19000

#def func1(fname):


def c_mod(REQ,conn,client_addr,num):
	first_line = REQ.split('\n')[0]

	if first_line.split(' ')[0] == "GET":
		url = first_line.split(' ')[1]

		http_pos = url.find("://")
		if (http_pos != -1):
			temp = url[(http_pos+3):]
			port_pos = temp.find(":")
			web_p = temp.find("/")
		else:
			temp = url

		if web_p != -1:
			pass
		else:
			web_p = len(temp)

		webserver = ""
		port = -1

		if (not (port_pos==-1 or web_p < port_pos)):
			port = int((temp[(port_pos+1):])[:web_p-port_pos-1])
			webserver = temp[:port_pos]

		else:
			port = 20000
			webserver = temp[:web_p]

		print "Connect to:", webserver, port

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		time.sleep(0.01)
		s.connect(("",port))


		REQ = REQ.split('\n')
		l1 = REQ[0].split(' ')
		lw = url[::-1]
		print

		l1[1] = (lw[:lw.find('/')+1])[::-1]
		REQ[0] = ' '.join(l1)
		REQ = '\n'.join(REQ)
		s.sendall(REQ)
		print "REQ After", REQ
		cache=''
		data=s.recv(4096*2)
		if data.split('\n')[0].split(' ')[1]!='304':
			cache+=data
			conn.send(data)
			while 1:
				data = s.recv(4096*2)

				if (len(data) <= 0):
					break
				else:
					conn.send(data)
					cache=cache+data


			if cache.split('\n')[0].split(' ')[1]!='404' and 'no-cache' not in cache.split('\n')[6]:
				#print("sdhgjsgdk\n\n")
				c_data[num]=cache
				c_time[num]=cache.split('\n')[5].split('Last-Modified: ')[1].strip('\r')
				c_count[num]=0

		else:

			###
			print(c_data[num])
			conn.send(c_data[num])
			c_count[num]=0
		s.close()
		time.sleep(1)


flag=0
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if (flag==0):
    	print "socket created"
    sock.bind((HOST, PORT)) # associate the socket to host and port
    sock.listen(5) # listenning
    flag+=1
    if(flag==1):
    	print "socket connected"
    #print flag
    print "Listening on port 19000" #serving
except socket.error, (value, message):
    if sock:
        sock.close()
    print "Could not open socket:", message
    sys.exit(1)
# Now getting REQs from client
tu = 1
while 1:
	# accepting the client REQ
	conn, client_addr = sock.accept()
	# read the http message from client

	REQ = conn.recv(4096*2)

	if not REQ:
		pass
	else:
		fname=REQ.split('\n')[0].split('://')[1].split('/')[1].split(' ')[0]
		print(fname)

	if REQ and fname in c_title.values():
		#num=func1(fname)
		for i,j in c_title.items():

			if j == fname:
				num=i
				break

		print(num)
		c_count[num]+=1

		if(c_count[num]<1):
			conn.send(c_data[num])

		else:
			ff=REQ.split('\n')
			kk='If-Modified-Since: '+c_time[num]
			ff.insert(1,kk)
			REQ='\n'.join(ff)
			c_mod(REQ,conn,client_addr,num)
	else:
		first_line = REQ.split('\n')[0]

		# extracting url from firstline of data
		if first_line and first_line.split(' ')[0] == "GET":
			url = first_line.split(' ')[1]

			http_pos = url.find("://")
			if (http_pos==-1):
				temp = url
			else:
				temp = url[(http_pos+3):]
			port_pos = temp.find(":")
			web_p = temp.find("/")
			if web_p == -1:
				web_p = len(temp)
			webserver = ""
			port = -1
			if (port_pos==-1 or web_p < port_pos):
				port = 20000
				webserver = temp[:web_p]
			else:
				port = int((temp[(port_pos+1):])[:web_p-port_pos-1])
				webserver = temp[:port_pos]
			print "Connect to:", webserver, port
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			time.sleep(0.01)
			s.connect(("",port))
			REQ = REQ.split('\n')
			l1 = REQ[0].split(' ')
			lw = url[::-1]
			l1[1] = (lw[:lw.find('/')+1])[::-1]
			REQ[0] = ' '.join(l1)
			REQ = '\n'.join(REQ)
			s.sendall(REQ)
			print "REQ After", REQ
			cache=''
			while 1:
				data = s.recv(4096)
				if (len(data) > 0):
					conn.send(data)
					cache=cache+data
				else:
					break


			if cache.split('\n')[0].split(' ')[1]!='404' and 'no-cache' not in cache.split('\n')[6]:
				print("sdhgjsgdk\n\n")
				k=(k+1)%3
				c_title[k]=fname
				c_data[k]=cache
				c_time[k]=cache.split('\n')[5].split('Last-Modified: ')[1]
				c_count[k]=int(0)
				print(c_time)
			print(cache)
			s.close()
			time.sleep(1)
	conn.close()
sock.close()
