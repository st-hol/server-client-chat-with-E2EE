import socket, threading, time, re

import DH_Endpoint as dh
import util

lock = threading.Lock()

shutdown = False
established = False
join = False
connected = False

opponent_public = 0
opponent_partial = 0
dh_endpoint = 0
my_partial = 0
full_key = 0

my_public = util.get_random_key()
print("my pub = ", my_public)
my_private = util.get_random_key()
print("my prvt = ", my_private)


def establishE2E(name, sock):
    global established
    global connected
    global opponent_partial
    global opponent_public
    global dh_endpoint
    global my_partial
    global full_key

    lock.acquire()
    while not established:
        try:
            while True:
                data, addr = sock.recvfrom(1024)

                if "public_key" in data.decode("utf-8") \
                        and re.findall(r'\d+', data.decode("utf-8"))[1] != 0 \
                        and opponent_public == 0:
                    numbers = re.findall(r'\d+', data.decode("utf-8"))
                    opponent_public = int(numbers[1])
                    print("opponent's PUBLIC key : ", opponent_public)

                    order = int(re.findall(r'#\d+#', data.decode("utf-8"))[0].strip("#")) == 0
                    # print("ord", re.findall(r'#\d+#', data.decode("utf-8"))[0].strip("#"),"  ")
                    dh_endpoint = dh.DH_Endpoint(my_public, opponent_public, my_private, order)
                    my_partial = dh_endpoint.generate_partial_key()
                    sock.sendto(("[" + alias + "] => user partial_key is " + str(my_partial)).encode("utf-8"), server)
                    # time.sleep(0.2)
                    connected = True
                    # continue

                if "partial_key" in data.decode("utf-8") \
                        and re.findall(r'\d+', data.decode("utf-8"))[1] != 0 \
                        and opponent_partial == 0:
                    numbers = re.findall(r'\d+', data.decode("utf-8"))
                    opponent_partial = int(numbers[1])
                    print("opponent's PARTIAL key : ", opponent_partial)
                    # time.sleep(0.2)
                    connected = True

                if opponent_partial != 0:
                    full_key = dh_endpoint.generate_full_key(opponent_partial)
                    print("my FULL key : ", full_key)
                    print("End-to-end connection established. you can chat now!"
                          + "\n--------------------------------------------------"
                          + "\n\n>")
                    established = True
                    break

                # End
                time.sleep(0.2)
        except:
            pass
    lock.release()


def receiving(name, sock):
    global opponent_public
    global dh_endpoint
    global my_partial
    global full_key

    # time.sleep(5)
    lock.acquire()
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

                try:
                    found = re.search('\d#(.+)', decrypt).group(1)
                except AttributeError:
                    # \d# not found in the original string
                    found = ''
                print(found)
                # End
                time.sleep(0.2)
        except:
            pass
    lock.release()


host = socket.gethostbyname(socket.gethostname())
port = 0
server = (host, 9090)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))
sock.setblocking(0)

alias = util.input_string_name()

establishSecureConnectionThread = threading.Thread(target=establishE2E, args=("E2EThread", sock))
establishSecureConnectionThread.start()
receivingThread = threading.Thread(target=receiving, args=("RecvThread", sock))
receivingThread.start()

# messaging
while not shutdown:
    if not join:
        sock.sendto(("[" + alias + "] => joined chat ").encode("utf-8"), server)
        join = True
    elif not connected:
        sock.sendto(("[" + alias + "] => my user public_key is " + str(my_public)).encode("utf-8"), server)
        # s.sendto(("[" + alias + "] => my user partial_key is " + str(my_partial)).encode("utf-8"), server)
        time.sleep(0.2)
    else:
        try:
            message = input(">\n")
            # print('[you]: ' + message)

            # Begin
            crypt = ""
            for i in message:
                crypt += chr(ord(i) ^ full_key)
            message = crypt
            # End

            if message != "":
                sock.sendto(("[" + alias + "] says: " + message).encode("utf-8"), server)

            time.sleep(0.2)
        except:
            sock.sendto(("[" + alias + "] <= left chat ").encode("utf-8"), server)
            shutdown = True

establishSecureConnectionThread.join()
receivingThread.join()
sock.close()
