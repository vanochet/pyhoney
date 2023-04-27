import os, sys


print("Default console installation for Honey Indev 1.1\n")

print("Please, select installation type:")
print("\n    1. Local installation (no admin rights required, ~/AppData/Roaming/*)")
print("\n    2. Global installation (admin rights required, C:/Program Files)(doesn't work for now)")
instype = input("\nType #: ")

if instype == "3":
	path = os.path.abspath("local")
if instype == "1":
	path = os.path.expanduser("~/AppData/Roaming")
if instype == "2":
	path = "C:/Program Files/Honey1.1"

dir_bin = path+"/bin"
dir_lib = path+"/lib/honey1.1"
dir_doc = path+"/share/honey1.1/doc"
dir_inc = path+"/include/honey1.1"
dir_inf = path+"/share/honey1.1/inf"

dir_setup = os.path.abspath("./ins").replace(" ", "?")


print("Installing packages\n")

os.system("%s -m pip install -r %s" %
	(sys.executable, dir_setup+"/modules.lst"))

print("\nDone\n")

print("Loading modules...\n")

import shutil

print("\nDone\n")

print("Copying Honey 1.1 binaries to \"%s\"\n" % dir_bin)

shutil.copytree("./bin", dir_bin, dirs_exist_ok=True)

print("\nDone\n")

print("Copying Honey 1.1 libraries to \"%s\"\n" % dir_lib)

shutil.copytree("./lib", dir_lib, dirs_exist_ok=True)

print("\nDone\n")

print("Copying Honey 1.1 documentation to \"%s\"\n" % dir_doc)

shutil.copytree("./doc", dir_doc, dirs_exist_ok=True)

print("\nDone\n")

print("Copying Honey 1.1 includes to \"%s\"\n" % dir_inc)

shutil.copytree("./inc", dir_inc, dirs_exist_ok=True)

print("\nDone\n")

print("Copying Honey 1.1 info to \"%s\"\n" % dir_inf)

shutil.copytree("./lib", dir_inf, dirs_exist_ok=True)

print("\nDone\n")
