import threading, time

def func1():
    for j in range (0, 10):
        print(str(time.ctime(time.time())) + " 1")
        time.sleep(0.5)


def func2():
    for j in range (0, 10):
        print(str(time.ctime(time.time())) + " 2")
        time.sleep(0.5)

print(str(time.ctime(time.time())) + " script started")

t1 = threading.Thread(target = func1(), name = " 1")
t2 = threading.Thread(target = func2(), name = " 2")

t1.start()
t2.start()

t1.join()
t2.join()

print (str(time.ctime(time.time())) + " over")