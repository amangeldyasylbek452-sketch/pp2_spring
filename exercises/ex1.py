# Convert degrees to radians
import math

a = int(input())
b = math.radians(a)
print(b)


#area of a trapezoid
a = int(input())
b = int(input())
h = int(input())
S = (a + b) * h / 2
print(S)


#area of regular polygon
n = int(input())
s = int(input())
S = n * s**2 / (4 * math.tan(math.pi / n))
print(S)


#area of a parallelogram
b = int(input())
h = int(input())
S = b * h
print(S)