import os
import sys

from pprint import pformat, pprint
from random import randint

from parglare import Grammar, Parser

import x
import y

from dictobj import *


class Linter:
    def __init__(self):
        self.using = []
        self.funcs = {}
        self.types = []
        self.varbs = []
        self.const = {}

    def out(self):
        return Dictobj(
            using = self.using.copy(),
            funcs = self.funcs.copy(),
            types = self.types.copy(),
            varis = self.varbs.copy(),
            packg = self.pkg,
            oform = self.oformat,
            const = self.const
        )

    def add_const(self, t, d):
        if t not in self.const.keys():
            self.const[t] = []
        self.const[t] += [d]

    def visit_root(self, node):
        for n in node:
            pprint(n)

            if n[0] == "format":
                self.oformat = n[1].split(".")
                self.oformat[-1] = self.oformat[-1][len("bits"):]
            if n[0] == "package":
                self.pkg = n[1]
            if n[0] == "using":
                self.using.append(n[1])
            if n[0] == "fn":
                name = n[1]
                args = self.visit_args(n[3])
                if len(n) == 7:
                    rett = self.visit_type(n[5])
                    body = self.visit_body(n[7])
                else:
                    rett = self.visit_type("none")
                    body = self.visit_body(n[5])
                self.funcs[name] = [name, args, body]

    def visit_args(self, node):
        node = x.flat(node)
        args = x.split(node, ",")
        return [self.visit_arg(arg) for arg in args]

    def visit_arg(self, node):
        node.remove(":")
        return node.copy()

    def visit_type(self, node):
        if node not in self.types:
            self.types.append(node)
        return node

    def visit_body(self, node):
        r = []
        node = node[1:][:-1]
        for l in node[0]:
            r += self.visit_line(l[0])
        return r.copy()

    def set_arg(self, fn, n):
        return ["!SVD", "ARG!%s!%d" % (fn, n)]

    def visit_line(self, n):
        print("L:", pformat(n))
        r = []
        if n[0] == "return":
            return [["!RET", n[1] if len(n)-1 else "0"]]

        if len(n) == 4 and n[1] == "(":
            print("LC:", pformat(n))
            for num, a in enumerate(x.flat(n[2])):
                print(a, is_str:=y.is_string(a))
                if is_str:
                    print("LCS:", y.to_string(a))
                    self.add_const("str", y.to_string(a))
                    r += [["!LOD", y.get_const("str", len(self.const["str"])-1)]]
                    r += [self.set_arg(n[0], num)]
            return [["!SVF", n[0]], *r, ["!CAL", n[0]]]

        if len(n) == 2:
            print("LD1:", pformat(n))
            if len(n[1]) == 1:
                print("LD2:", pformat(n))
                if len(n[1][0]) == 2:
                    print("LD3:", pformat(n))
                    if n[1][0][0] == "=":
                        print("LD4:", pformat(n))
                        r = []
                        name = n[0][0]
                        data = n[1][0][1]
                        if len(n[0]) == 3:
                            dtyp = n[0][2]
                            self.varbs.append([name, dtyp])
                            r = [["!DEF", name, dtyp]]
                            print("LD5:", pformat(n))
                        return [*r, ["!SVD", name, data]]

        return r
