import socket, threading, time, random, re
import DH_Endpoint as dh

key = 8194
shutdown = False
join = False
connected = False

my_public = random.randint(1, 101)
print("my pub = ", my_public)
my_private = random.randint(1, 101)
print("my prvt = ", my_private)

opponent_public = 0
opponent_partial = 0
dh_endpoint = 0
my_partial = 0
full_key = 0


def establishE2E(name, sock):
    global connected
    global opponent_partial
    global opponent_public
    global dh_endpoint
    global my_partial
    global full_key

    while not shutdown:
        try:
            while True:
                data, addr = sock.recvfrom(1024)

                if "public_key" in data.decode("utf-8") \
                        and re.findall(r'\d+', data.decode("utf-8"))[0] != 0 \
                        and opponent_public == 0:
                    numbers = re.findall(r'\d+', data.decode("utf-8"))
                    opponent_public = int(numbers[0])
                    print("PUBLIC opponent key : ", opponent_public)
                    dh_endpoint = dh.DH_Endpoint(my_private, opponent_public, my_private)
                    my_partial = dh_endpoint.generate_partial_key()
                    sock.sendto(("[" + alias + "] => user partial_key is " + str(my_partial)).encode("utf-8"), server)
                    time.sleep(0.2)
                    connected = True
                    continue

                if "partial_key" in data.decode("utf-8") \
                        and re.findall(r'\d+', data.decode("utf-8"))[0] != 0 \
                        and opponent_partial == 0:
                    numbers = re.findall(r'\d+', data.decode("utf-8"))
                    opponent_partial = int(numbers[0])
                    print("PARTIAL opponent key : ", opponent_partial)
                    time.sleep(0.2)
                    connected = True

                if my_partial != 0 and my_public != 0 and my_private != 0 and opponent_public != 0 and opponent_partial != 0:
                    full_key = dh_endpoint.generate_full_key(opponent_partial)
                    print("MY FULL:", full_key)
                    break

                # End
                time.sleep(0.2)
        except:
            pass


def receiving(name, sock):
    global opponent_public
    global dh_endpoint
    global my_partial
    global full_key

    while not shutdown:
        try:
            while True:
                data, addr = sock.recvfrom(1024)

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
                        decrypt += chr(ord(i) ^ full_key)
                print(decrypt)
                # End
                time.sleep(0.2)
        except:
            pass


host = socket.gethostbyname(socket.gethostname())
port = 0
server = (host, 9090)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0)


def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))


alias = input("Set your name ")
while alias == "" or hasNumbers(alias):
    if alias == "" or hasNumbers(alias):
        print("This is not a valid name. Only [A-Za-z] allowed!")
    alias = input("Set your name ")

# receivingThread = threading.Thread(target=receiving, args=("RecvThread", s))
establishSecureConnectionThread = threading.Thread(target=establishE2E, args=("SecurThread", s))
# receivingThread.start()
establishSecureConnectionThread.start()


# messaging
while not shutdown:
    if not join:
        s.sendto(("[" + alias + "] => joined chat ").encode("utf-8"), server)
        join = True
    elif not connected:
        s.sendto(("[" + alias + "] => my user public_key is " + str(my_public)).encode("utf-8"), server)
        # s.sendto(("[" + alias + "] => my user partial_key is " + str(my_partial)).encode("utf-8"), server)
        time.sleep(0.2)
    else:
        try:
            message = input()

            # Begin
            crypt = ""
            for i in message:
                crypt += chr(ord(i) ^ full_key)
            message = crypt
            # End

            if message != "":
                s.sendto(("[" + alias + "] says: " + message).encode("utf-8"), server)

            time.sleep(0.2)
        except:
            s.sendto(("[" + alias + "] <= left chat ").encode("utf-8"), server)
            shutdown = True

# receivingThread.join()
establishSecureConnectionThread.join()
s.close()
