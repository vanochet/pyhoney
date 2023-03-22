from dictobj import *
from parser import *
from random import randint


SIMPLE_BINOPS = (
    "add",
    "sub",
    "or",
    "and",
    "xor",
    "mul"
)

SIMPLE_UNOPS = (
    "neg",
    "not"
)

SIMPLE_OPERS = (
    "integer",
    "string",
    "label"
)

COMPLEX_BINOPS = (
    "div",
    "pow",
    "ind"
)

MUTABLE = (
    "integer"
)


class Asm:
    def visit_root(n):
        for n in n.nodes:
            if n.type == "cal":
                ...


class Label(Dictobj):
    dct = {
        "name": "",
        "type": "",
        "init": "",
        "func": ""
    }


class Function(Dictobj):
    dct = {
        "as_code": "",
        "locals": {},
        "linter": ...,
        "name": "_",
        "clas": "",
        "args": [],
        "rtyp": "",
        "body": ...
    }
    
    def get_as_name(self):
        return "fn$%s$%s$%s" % (
            self.linter.data.package,
            self.clas,
            self.name
        )
    
    def get_as_text(self):
        text = self.get_as_header()
        self.visit_node(self.body)
        text += self.as_code

    def get_as_header(self):
        word = self.linter.get_word()
        rp = self.linter.get_reg_pre()
        rax, rbx, rcx, rdx = rp+"ax", rp+"bx", rp+"cx", rp+"dx"
        rsp, rbp = rp+"sp", rp+"bp"

        header = self.get_as_name()+":\n"
        header += "\n".join(("    push %s 0" % word)
            for i in range(len(self.locals)))
        header += "    push %s %s\n" % (word, rbp)
        header += "    mov %s, %s\n" % (rbp, rsp)

        return header

    def get_as_return(self):
        word = self.linter.get_word()
        rp = self.linter.get_reg_pre()
        rax, rbx, rcx, rdx = rp+"ax", rp+"bx", rp+"cx", rp+"dx"
        rsp, rbp = rp+"sp", rp+"bp"

        ret += "    pop %s %s\n" % (word, rbp)
        if self.locals:
            ret += '    lea %s %s, [%s*%s]\n' % (word, rsp, rsp,
                8*len(self.locals))
            ret += "\n    ret\n"

        return ret

    def visit_call(self, node):
        word = self.linter.get_word()
        rp = self.linter.get_reg_pre()
        rax, rbx, rcx, rdx = rp+"ax", rp+"bx", rp+"cx", rp+"dx"
        rsp, rbp = rp+"sp", rp+"bp"
        for arg in node.args:
            self.visit_node(arg)
        if args:
            self.add_instr("    add %s %s, %s\n" %
                (word, rsp, 8*len(node.args)))
        self.add_instr("    push %s %s\n" % (word, rax))

    def gen_binop(self, op, value=1, ax=None, dx=None):
        word = self.linter.get_word()
        rp = self.linter.get_reg_pre()
        rax, rbx, rcx, rdx = rp+"ax", rp+"bx", rp+"cx", rp+"dx"
        rsp, rbp = rp+"sp", rp+"bp"
        if ax is None:
            ax = rax
        if dx is None:
            dx = rdx
        self.add_instr("    pop %s %s\n" % (word, dx))
        self.add_instr("    pop %s %s\n" % (word, ax))
        if value:
            self.add_instr("    %s %s %s, %s\n" %
                (op, word, ax, bx))
            self.add_instr("    push qword %s\n" % rax)

    def gen_id(self):
        int_id = randint(0x1000, 0xFFFF)
        hex_id = hex(int_id)
        str_id = hex_id.removeprefix("0x").upper()
        return str_id

    def add_label(self, name):
        self.add_instr("%s:\n" % name)

    def visit_node(self, node):
        word = self.linter.get_word()
        rp = self.linter.get_reg_pre()
        rax, rbx, rcx, rdx = rp+"ax", rp+"bx", rp+"cx", rp+"dx"
        rsp, rbp = rp+"sp", rp+"bp"
        if node.type in ("callargs", "body"):
            (self.visit_node(node) for node in node.args)
        if node.type == "return":
            self.add_instr(self.get_as_return())
        if node.type == "def":
            self.locals[node.name] = Label(name=node.name,
                type=node.dtyp, init=node.value, func=self)
        if node.type in SIMPLE_BINOPS:
            self.gen_binop(node.type)
        if node.type in COMPLEX_BINOPS:
            if node.type == "pow":
                label = "loc_op_pow_"+self.gen_id()
                self.add_instr("    push %s\n" % rcx)
                self.add_instr("    pop %s %s\n" % (word, rcx))
                self.add_instr("    pop %s %s\n" % (word, rax))
                self.add_label(label)
                self.gen_binop(node.type, node.a, node.a)
                self.add_instr("    pop %s %s\n" % (word, rax))
                self.add_instr("    loop %s\n" % label)
                self.add_instr("    pop %s %s\n" % (word, rcx))
                self.add_instr("    push %s %s\n" % (word, rax))
            if node.type == "ind":
                self.gen_binop(";", 0)
                self.add_instr("    mov %s %s, %s\n" % (word, rbx, rax))
                self.add_instr("    mov %s %s, %s\n" % (word, rcx, rdx))
                self.add_instr("    push %s %d %s %s\n" %
                    (word, self.linter.get_word_size(), word, rax))
                self.gen_binop(";", 0)
                self.add_instr("    mul %s %s\n" % (word, rdx))
                self.add_instr("    pop %s %s\n" % (word, rax))
                self.add_instr("    add %s %s, %s\n" %
                    (word, rbx, rax))
                self.add_instr("    push %s %s\n" % (word, rbx))
            if node.type == "div":
                self.add_instr("    pop %s %s\n" % (word, rdx))
                self.add_instr("    pop %s %s\n" % (word, rax))
                self.add_instr("    div %s %s\n" % (word, rdx))
                self.add_instr("    push %s %s\n" % (word, rax))
            if node.type in SIMPLE_OPERS:
                if node.type == "integer":
                    self.add_instr("    push %s %s" %
                        (word, node.value))
                if node.type == "string":
                    self.add_instr("    push %s %s" %
                        (word, node.value))
                if node.type == "label":
                    name = node.name
                    local = name in self.locals.keys()
                    if local:
                        labl = self.linter.globals[node.name]
                    else:
                        labl = self.linter.globals[node.name]
                    mutbl = labl.type not in MUTABLE

                    self.add_instr("    push %s %s" %
                        (word, name if mutbl else ("[%s]" % name)))



class Linter:
    parser = None
    clas = ""

    data = Dictobj(
        format="binary-ia86-16-raw",
        package="main",
        uses=[],
        funcs=[]
    )

    def __init__(self, parser):
        self.parser = parser

    def get_word(self):
        return {
            "16": "word",
            "32": "dword",
            "64": "qword"
        }[self.data.format.split("-")[2]]

    def get_reg_pre(self):
        return {
            "16": "",
            "32": "e",
            "64": "r"
        }[self.data.format.split("-")[2]]
    
    def get_word_size(self):
        return {
            "16": 2,
            "32": 4,
            "64": 8
        }[self.data.format.split("-")[2]]

    def visit_funcs(self):
        for f in self.parser.data.funcs:
            self.data.funcs.append(
                Function(linter=self, name=f.name, args=f.args, rtyp=f.rtyp, body=f.body, clas=self.clas))
