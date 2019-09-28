import socket, time

host = socket.gethostbyname(socket.gethostname())
port = 9090

clients = []

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind((host,port))

quit = False
print("[ Server Started ]")

while not quit:
	try:
		data, addr = s.recvfrom(1024)

		itsatime = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())

		if addr not in clients:
			if len(clients) >= 2:
				s.sendto("room is full".encode("UTF-8"), addr)
				print("[" + addr[0] + "]=[" + str(addr[1]) + "]=[" + itsatime + "]/", end="")
				print(data.decode("utf-8"))
				continue
			clients.append(addr)

		print("["+addr[0]+"]=["+str(addr[1])+"]=["+itsatime+"]/", end="")
		print(data.decode("utf-8"))

		for client in clients:
			# if addr != client:
			# 	s.sendto(data,client)
			s.sendto(data, client)
	except:	
		print("\n[ Server Stopped ]")
		quit = True
		
s.close()