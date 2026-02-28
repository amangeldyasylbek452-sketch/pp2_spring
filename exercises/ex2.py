#generates a square of the size n
def square(n):
    for i in range(n):
        yield i * i

a = int(input())
for i in square(a+1):
    print(i)


#generates the even numbers up to n
def even(n):
    for i in range(n+1):
        if i % 2 == 0:
            yield i
a = int(input())
for i in even(a):
    print(i)



#function with generator which can iterate the numbers, which are divisible by 3 and 4, up from 0 to n
def div(n):
    for i in range(n+1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

a = int(input())
for i in div(a):
    print(i)


#generator called squeres to yield the squeres for all numbers from a to b
def squares(a, b):
    for i in range(a, b+1):
        yield i * i

a = int(input())
b = int(input())
for i in squares(a, b):
    print(i)


#generator that returns all numbers from (n) down to 0.
def down(n):
    for i in range(n, -1, -1):
        yield i
a = int(input())
for i in down(a):
    print(i)