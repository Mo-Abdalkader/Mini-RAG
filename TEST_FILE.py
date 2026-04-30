from random import random, randint


def get_random_number(num):
    return ["*" * i for i in range(1, num+1)]


print(list(map(get_random_number, {1:2, 2:3, 3:4}.values())))