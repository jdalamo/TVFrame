import os

filename = "hey.png"

name, ext = os.path.splitext(filename)
print(ext[0])
ext.lstrip('.')
print(ext)