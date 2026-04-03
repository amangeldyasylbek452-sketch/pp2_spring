import os
os.remove("demofile.txt")


if os.path.exists("demofile.txt"):
  os.remove("demofile.txt")
else:
  print("The file does not exist")


import os
os.rmdir("myfolder")