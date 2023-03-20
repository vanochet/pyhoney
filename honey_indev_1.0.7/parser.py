from parglare import Parser as Parse, Grammar
from dictobj import *


gram = r"""

sroot: sany*;

sany: sformat
    | suse
    | sfn
    | sdefine;

sformat: "format" tname ";";
suse: "using" tname ";";
sfn: "fn" tname "(" sargs? ")" "->" tname sbody;
sargs: sarg ("," sarg)*;
sarg: tname ":" tname;
sbody: "{" sline* "}";
sline: (scall | sequal | sdefine | sreturn) ";";
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

"""


def flat(a):
    r = []
    for i in a:
        if isinstance(i, list):
            r += flat(i)
        else:
            r.append(a)
    return r.copy()


class Parser:
    parser = None
    grammar = None
    actions = None
    syntree = None
    
    def __init__(self, grammar):
        self.grammar = Grammar.from_string(grammar)
    
    def init(self):
        self.parser = Parse(self.grammar, actions=self.actions)


class CodeParser(Parser):
    data = Dictobj(
        format = "binary-x86-raw",
        uses = [],
        funcs = []
    )
    
    def __init__(self, grammar):
        self.grammar = Grammar.from_string(grammar)
    
    def init(self):
        self.parser = Parse(self.grammar, actions=self.actions)
    
    def burn(self):
        self.actions = dict(
            sroot=self.sroot,
            sany=self.sany,
            sformat=self.sformat,
            suse=self.suse,
            sfn=self.sfn,
            sargs=self.sargs,
            sarg=self.sarg,
            sbody=self.sbody,
            sline=self.sline,
            scall=self.scall,
            scallargs=self.scallargs,
            sequal=self.sequal,
            sdefine=self.sdefine,
            sreturn=self.sreturn,
            sexpr=self.sexpr(),
            ssequence=self.ssequence
        )
    
    def sroot(self, _, n):
        return Dictobj(nodes=n.copy())
    
    def sany(self, _, n):
        return n[0]
    
    def sformat(self, _, n):
        self.data.format = n[1]
        return _
        
    def suse(self, _, n):
        self.data.uses.append(n[1])
        return _
    
    def sfn(self, _, n):
        name = n[1]
        args = n[3]
        rtyp = n[6]
        body = n[7]
        self.data.funcs.append(Dictobj(
            name=name,
            args=args,
            rtyp=rtyp,
            body=body
        ))
        return _
    
    def sargs(self, _, n):
        args = flat(n)
        while "," in args:args.remove(",")
        while [] in args:args.remove([])
        return args.copy()
    
    def sarg(sslf, _, n):
        return Dictobj(name=n[0], dtyp=n[2])
    
    def sbody(self, _, n):
        return Dictobj(type="body", content=n[1:][:-1])
    
    def sline(self, _, n):
        return n[0]
    
    def scall(self, _, n):
        name = n[0]
        args = n[2] if n[2] else []
        return Dictobj(type="cal", name=name, args=args)
    
    def scallargs(self, _, n):
        args = flat(n)
        while "," in args:args.remove(",")
        while [] in args:args.remove([])
        return Dictobj(type="callargs", args=args.copy())
    
    def sequal(self, _, n):
        name = n[0]
        vale = n[2]
        return Dictobj(type="equ", name=name, value=vale)
    
    def sdefine(self, _, n):
        name = n[0].name
        dtyp = n[0].dtyp
        vale = Dictobj(type="ptr", value=0)
        if n[1]:
            vale = n[1]
        return Dictobj(type="def", name=name, dtyp=dtyp, value=vale)
    
    def sreturn(self, _, n):
        return Dictobj(type="ret", value=n[1] if n[1] else Dictobj(type="integer", value=0))
    
    def ssequence(self, _, n):
        return n[1]
    
    def sexpr(self):
        return [
            lambda _, n: n[1],
            lambda _, n: Dictobj(type="ind", seq=n[0], index=n[2]),
            lambda _, n: Dictobj(type="pow", a=n[0], b=n[2]),
            lambda _, n: Dictobj(type="neg", op=n[1]),
            lambda _, n: Dictobj(type="mul", a=n[0], b=n[2]),
            lambda _, n: Dictobj(type="div", a=n[0], b=n[2]),
            lambda _, n: Dictobj(type="add", a=n[0], b=n[2]),
            lambda _, n: Dictobj(type="sub",a=n[0], b=n[2]),
            lambda _, n: Dictobj(type="not", a=n[0], b=n[2]),
            lambda _, n: Dictobj(type="or", a=n[0], b=n[2]),
            lambda _, n: Dictobj(type="and", a=n[0], b=n[2]),
            lambda _, n: Dictobj(type="xor", a=n[0], b=n[2]),
            lambda _, n: Dictobj(type="integer", value=n[0]),
            lambda _, n: Dictobj(type="string", value=n[0]),
            lambda _, n: Dictobj(type="label", name=n[0]),
            lambda _, n: n[0]
        ]


def test():
    parser = CodeParser(gram)
    
    with open('test.hny', 'rt') as f:
        code = f.read()
    
    parser.burn()
    parser.init()
    
    parser.syntree = parser.parser.parse(code)
    
    return parser
