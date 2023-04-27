import os
import sys
import pathlib

from pprint import pformat, pprint

from parglare import Grammar, Parser

import x

from parser  import *
from linter  import *
from asm     import *


debug = "--debug" in sys.argv
help = '--help' in sys.argv or len(sys.argv) == 1

if help:
    print("help not implemented yet")
    sys.exit(0)

path = str(pathlib.Path(sys.executable).parent.resolve())

ifile = sys.argv[-1]
ofile = ifile.split("/")[-1].split("\\")[-1]
ofile = ofile[:-1-len(ofile.split(".")[-1])]+".hna"

if debug:
	print(ifile, ofile)

try:
	with open(ifile, "rt") as f:
		icode = f.read()
except Exception as e:
	print("Error:", e)
	sys.exit(3)

parser = Parser(Grammar.from_string(syntax))
tree = parser.parse(icode)

if debug:
	pprint(tree)

linter = Linter()
linter.visit_root(tree)

if debug:
	pprint(linter.__dict__)

asm = Asm()
asm.build(linter.out())

if debug:
	print(asm.code[1:])

with open(ofile, "wt") as f:
	f.write(asm.code[1:])

if not "--hna" in sys.argv:
	os.system(path+"/hna "+ofile)
	os.unlink(ofile)
