import re


def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))


def inputStringName():
    alias = input("Set your name ")
    while alias == "" or hasNumbers(alias):
        if alias == "" or hasNumbers(alias):
            print("This is not a valid name. Only [A-Za-z] allowed!")
        alias = input("Set your name ")
    return alias