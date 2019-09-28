import socket, threading, time

class RoomIsFullException(Exception):
   """Raised when the room is full"""
   pass

key = 8194

shutdown = False
join = False
roomIsFull = False

def receiving(name, sock):
    global roomIsFull
    global shutdown
    while not shutdown:
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                # print(data.decode("utf-8"))

                if data.decode("utf-8") == "room is full":
                    raise RoomIsFullException

                # Begin
                decrypt = ""
                k = False
                for i in data.decode("utf-8"):
                    if i == ":":
                        k = True
                        decrypt += i
                    elif k == False or i == " ":
                        decrypt += i
                    else:
                        decrypt += chr(ord(i) ^ key)
                print(decrypt)
                # End
                time.sleep(0.2)
        except RoomIsFullException:
            print("Sorry room is full. You will be disconnected.")
            roomIsFull = True
            shutdown = True
            break
        except:
            pass


host = socket.gethostbyname(socket.gethostname())
port = 0

# [192.168.1.3]
# server = ("192.168.0.101",9090)
# server = ("192.168.1.3", 9090)
server = (host, 9090)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0)

alias = input("Set your Name: ")

rT = threading.Thread(target=receiving, args=("RecvThread", s))
rT.start()

while not shutdown:
    if roomIsFull:
        s.sendto(("[" + alias + "] => can not join cause room is full").encode("utf-8"), server)
        shutdown = True
        continue

    if not join:
        s.sendto(("[" + alias + "] => joined chat ").encode("utf-8"), server)
        join = True
    else:
        try:
            message = input()

            # Begin
            crypt = ""
            for i in message:
                crypt += chr(ord(i) ^ key)
            message = crypt
            # End

            if message != "":
                s.sendto(("[" + alias + "] says: " + message).encode("utf-8"), server)

            time.sleep(0.2)
        except:
            s.sendto(("[" + alias + "] <= left chat ").encode("utf-8"), server)
            shutdown = True

rT.join()
s.close()
