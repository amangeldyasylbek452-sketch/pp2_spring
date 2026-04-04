a = 33
b = 200
if b > a:
  print("b is greater than a")

a = 33
b = 33
if b > a:
  print("b is greater than a")
elif a == b:
  print("a and b are equal")

a = 200
b = 33
if b > a:
  print("b is greater than a")
elif a == b:
  print("a and b are equal")
else:
  print("a is greater than b")

a = 5
b = 2
if a > b: print("a is greater than b")

a = 200
b = 33
c = 500
if a > b and c > a:
  print("Both conditions are True")

x = 41

if x > 10:
  print("Above ten,")
  if x > 20:
    print("and also above 20!")
  else:
    print("but not above 20.")

age = 16

if age < 18:
  pass # TODO: Add underage logic later
else:
  print("Access granted")

