import re
import random


def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))


def input_string_name():
    alias = input("Set your name ")
    while alias == "" or has_numbers(alias):
        if alias == "" or has_numbers(alias):
            print("This is not a valid name. Only [A-Za-z] allowed!")
        alias = input("Set your name ")
    return alias


def get_random_key():
    return random.randint(150, 2000)

