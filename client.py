import socket, threading, time, re
import tkinter

import DH_Endpoint as dh
import util

lock = threading.Lock()

shutdown = False
established = False
join = False
connected = False
alias = ""

opponent_public = 0
opponent_partial = 0
dh_endpoint = 0
my_partial = 0
full_key = 0


def on_closing(event=None):
    my_msg.set("{quit}")
    send()


def send(event=None):  # event binded
    msg = my_msg.get()
    my_msg.set("")  # Clear input
    sock.sendto(("[" + alias + "]" + msg).encode("utf-8"), server)
    msg_list.insert(tkinter.END, "[you] :" + msg)
    if msg == "{quit}":
        sock.close()
        top.quit()


top = tkinter.Tk('300x900')
top.title("client-server chat with E2EE")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages
my_msg.set("")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate
#
msg_list = tkinter.Listbox(messages_frame, height=15, background='black', fg='green', width=50,
                           yscrollcommand=scrollbar.set, font=("Lucida Console", 14))
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()
entry_field = tkinter.Entry(top, textvariable=my_msg, width=30, font=("Lucida Console", 10))
entry_field.bind("<Return>", send)  # send entry if enter pressed
entry_field.pack()
send_button = tkinter.Button(top, text="ВІДПРАВИТИ", command=send, background='blue', fg='white', font=("Lucida Console", 14))
send_button.pack()
top.protocol("WM_DELETE_WINDOW", on_closing)

# alias = util.input_string_name()


host = socket.gethostbyname(socket.gethostname())
port = 0
server = (host, 9090)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))
sock.setblocking(0)


def establishE2E(name, sock):
    global established, connected
    global opponent_partial, opponent_public, dh_endpoint, my_partial, full_key
    global alias, my_public, my_private

    lock.acquire()

    my_public = util.get_random_key()
    print("my pub = ", my_public)
    my_private = util.get_random_key()
    print("my prvt = ", my_private)

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
                    # print(int(re.findall(r'#\d+#', data.decode("utf-8"))[0].strip("#")))
                    # if order == 0:
                    #     alias = "first"
                    # else:
                    #     alias = "second"
                    alias = "opponent"
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
    msg_list.insert(tkinter.END, "End-to-end connection established. \nYou can chat now!")
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
                msg_list.insert(tkinter.END, found)
                # End
                time.sleep(0.2)
        except:
            pass
    lock.release()


def sending(name, sock):
    global shutdown, join

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


establishSecureConnectionThread = threading.Thread(target=establishE2E, args=("E2EThread", sock))
establishSecureConnectionThread.start()
receivingThread = threading.Thread(target=receiving, args=("RecvThread", sock))
receivingThread.start()
sendingThread = threading.Thread(target=sending, args=("SendThread", sock))
sendingThread.start()

# top.protocol("WM_DELETE_WINDOW", on_closing)


tkinter.mainloop()  # Starts GUI execution.
establishSecureConnectionThread.join()
receivingThread.join()
sendingThread.join()
sock.close()






















### messaging
#
# def send():
#     global shutdown, join
#
#     if not shutdown:
#         if not join:
#             sock.sendto(("[" + alias + "] => joined chat ").encode("utf-8"), server)
#             join = True
#         elif not connected:
#             sock.sendto(("[" + alias + "] => my user public_key is " + str(my_public)).encode("utf-8"), server)
#             # s.sendto(("[" + alias + "] => my user partial_key is " + str(my_partial)).encode("utf-8"), server)
#             time.sleep(0.2)
#         else:
#             try:
#                 message = input(">\n")
#                 # print('[you]: ' + message)
#
#                 # Begin
#                 crypt = ""
#                 for i in message:
#                     crypt += chr(ord(i) ^ full_key)
#                 message = crypt
#                 # End
#
#                 if message != "":
#                     sock.sendto(("[" + alias + "] says: " + message).encode("utf-8"), server)
#
#                 time.sleep(0.2)
#             except:
#                 sock.sendto(("[" + alias + "] <= left chat ").encode("utf-8"), server)
#                 shutdown = True
#