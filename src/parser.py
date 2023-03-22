from parglare import Parser as Parse, Grammar
from pprint import pformat, pprint
from dictobj import *


syntax = r"""

sroot: sany*;

sany: sformat
    | suse
    | sfn
    | sasmfn
    | simport
    | tcomment
    | sdefine;

sformat: "format" tname ";";
suse: "using" tname ";";
sfn: "fn" tname "(" sargs? ")" "->" tname sbody;
sargs: sarg ("," sarg)*;
sarg: tname ":" tname;
sbody: "{" sline* "}";
sline: (scall | sequal | sdefine | sreturn | tcomment) ";";
scall: tname "(" scallargs? ")";
scallargs: sexpr ("," sexpr)*;
sequal: tname "=" sexpr ";";
sdefine: sarg ("=" sexpr)* ";";
sreturn: "return" sexpr?;
sexpr:
     "(" sexpr ")"
    |(ssequence | tname) "[" tinteger "]"
    |sexpr "*" "*" sexpr
    |"-" sexpr
    |sexpr "*" sexpr
    |sexpr "/" sexpr
    |sexpr "+" sexpr
    |sexpr "-" sexpr
    |"!" sexpr
    |sexpr "&" sexpr
    |sexpr "|" sexpr
    |sexpr "^" sexpr
    |tinteger
    |tstring
    |tname
    |ssequence;
ssequence:
    "<" scallargs ">";

terminals

tstring: /"[^"]*"/;
tname: /([A-Za-z_]\w*\.)*[A-Za-z_]\w*/;
tinteger: /00?|[1-9]\d*/;
tcomment: /\/\*[^(\*\/)]\*\//;
tasm: /asm\s*\{[^\}]\}/;

"""


def flat(a):
    r = []
    for i in a:
        if isinstance(i, list):
            r += flat(i)
        else:
            r.append(a)
    return r.copy()


class Node:
    type = "root"
    data = {}
    nods = ()

    def __init__(self, typ, data, nods):
        self.typ = str(typ)
        self.data = {}
        self.data.update(data)
        self.nods = list(nods).copy()

    def __str__(self):
        nods = "\n".join(tuple(str(i) for i in self.nods))
        nods = nods.replace("\n", "\n    ")
        return """Node <%s>
    %s
%s""" % (self.type, pformat(self.data), nods)
    
    __repr__ = __str__


grammar = Grammar.from_string(syntax)


def parse_sargs(_, n):
    n = flat(n)
    while "," in n: n.remove(",")
    return n.copy()

def parse_define(_, n):
    dtype, name = n[0].data["dtype"], n[0].data["name"]
    ivalue = n[1][1] if n[1] is not None else "STRUC_%s_VOID"
    return Node("defneo",
        {"lrnode": _, "dtype": dtype,
        "name": name, "ivalue": ivalue}, [])


actions = {
    "sroot": lambda _, n: Node("root", {"lrnode": _}, n),
    "sany": lambda _, n: n[0],
    "sformat": lambda _, n: Node("oformat",
        {"lrnode": _, "oformat": n[1]}, []),
    "suse": lambda _, n: Node("stdinc",
        {"lrnode": _, "stdlib": n[1]}, []),
    "sfn": lambda _, n: Node("func",
        {"lrnode": _, "pkg": "", "clas": "", "name": n[1],
        "sargs": n[3], "rtype": n[6]}, list(n[7]).copy()),
    "sargs": parse_sargs,
    "sarg": lambda _, n: Node("vardef",
        {"lrnode": _, "name": n[0], "dtype": n[2]}),
    "sbody": lambda _, n: n[1],
    "sline": lambda _, n: flat(n)[0]
    "scall": lambda _, n: Node("call",
        {"lrnode": _, "name": n[0], "args": n[2]}, []),
    "scallargs": parse_sargs,
    "sequal": Node("assign",
        {"lrnode": _, "target": n[0], "value": n[2]}),
    "sdefine": parse_define,
    "sreturn": lambda _, n: Node("return",
        {"lrnode": _, "rvalue": n[1]})
}
