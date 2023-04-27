import re, sys, os, pathlib
from pprint import pprint


help = '--help' in sys.argv or len(sys.argv) == 1

if help:
    print("help not implemented yet")
    sys.exit(0)

file = sys.argv[-1]
path = str(pathlib.Path(sys.executable).parent.resolve())
home = os.path.expanduser("~")

outfile = file.split("/")[-1].split("\\")[-1]
outfile = outfile[:-len(outfile.split(".")[-1])-1]


with open(file, "rt") as f:
    code = f.read()

DEBUG = True


class Lexer:
    code: list[str]
    tokens: list[list[str]]
    strs: list[str]

    def __init__(self, code):
        self.tokens, self.pos = [], 0
        code = code.strip()
        self.strs = re.findall(r'"[^"]*"', code)
        if DEBUG:
            print('Pretokenized strings:')
            pprint(self.strs)
        for n, i in enumerate(self.strs):
            code = code.replace(i, "_____S%s_____"
                % n)
        code = code.splitlines()
        for line in code:
            self.tokens += [list(re.split(r"(\b|\s)", line))]
            for i, v in enumerate(self.tokens[-1]):
                self.tokens[-1][i] = \
                    self.tokens[-1][i].strip()
                if v.startswith('_____S'):
                    if v.endswith('_____'):
                        self.tokens[-1][i] = \
                            self.strs[eval(
                                v[6:][:-5]
                            )]
            while '' in self.tokens[-1]:
                self.tokens[-1].remove('')
        for i in self.tokens:
            if not i:
                self.tokens.remove(i)
        if DEBUG:
            print("Pretokenized code parts:")
            pprint(self.tokens)


strucs = {
    "format": ["!", "FORMAT", 1],
    "arch":   ["!", "ARCH", 1  ],
    "bits":   ["!", "BITS", 1  ],
    "base":   ["!", "ORG", 1],
    "stack":  ["!", "STACK", 1],
    "using":  ["!", "USING"],
    "proc":   ["!", "PROC", 1, "(", 0, ")"],
    "func":   ["!", "FUNC", 1, "(", 0, ")", 0],
    "end":    ["!", "END"]
}


class Parser:
    lexer: Lexer
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.using = []
        self.state = ''
        self.procs = []
        self.funcs = []
        self.consts = []

        self.visit_root(self.lexer.tokens)

    def visit_root(self, rnod):
        skip = 0

        for ln in rnod:

            if skip:
                skip -= 1
                continue

            if ln[:2] == ['!', 'FORMAT']:
                self.format = ln[2]

            if ln[:2] == ['!', 'ARCH']:
                self.arch = ln[2]

            if ln[:2] == ['!', 'BITS']:
                self.bits = ln[2]

            if ln[:2] == ['!', 'ORG']:
                self.base = ln[2]

            if ln[:2] == ['!', 'STACK']:
                self.stack = ln[2]

            if ln[:2] == ['!', 'PACKAGE']:
                self.pkg = ln[2]

            if ln[:2] == ['!', 'USING']:
                self.enter('using')

            if len(ln) == 1 and \
                self.state == '~using':
                    self.using.append(ln[0])

            if ln[:2] == ['!', 'END']:
                self.exit()
            if ln[0] == "!" and \
                    ln[1] == 'PROC' and \
                    ln[3] == '(':
                name = ln[2]
                args = self.extract(ln, "(", ")")
                skip = self.new_proc(name, args, self.split(rnod, ln)[1])

            if ln[0] == "!" and \
                    ln[1] == "FUNC" and \
                    ln[3] == "(":
                name = ln[2]
                args = self.extract(ln, "(", ")")
                rtyp = self.split(ln, ")")
                skip = self.new_func(name, args,
                    rtyp, self.split(rnod, ln)[1])

            if ln[:2] == ["!", "CONST"]:
                self.visit_const(ln[2:])

    def visit_const(self, rnod):
        self.consts += [[self.visit_type(
            self.extract(rnod, "(", ")")),
            self.visit_expr(self.split(rnod, ")")[1])]]

    def visit_expr(self, rnod):
        return "".join(tuple(rnod))

    def new_proc(self, name, args, body_nt): # nt - not terminized
        self.procs += [[name, self.visit_args(args),
                    self.visit_body(body_nt)]]
        return len(self.procs[-1][2])

    def new_func(self, name, args, rtyp, body_nt): # nt - not terminized
        self.procs += [[name, self.visit_args(args),
                    self.visit_type(rtyp), self.visit_body(body_nt)]]
        return len(self.procs[-1][3])

    def visit_body(self, rnod):
        body = []
        for ln in rnod:
            ln = ln[1:]
            if ln[0] == "END":
                break
            cl = ln[0]
            pm = "".join(tuple(ln[1:]))
            body += [[cl, pm]]
        return body.copy()

    def visit_args(self, rnod):
        rnod = self.split(rnod, ",")
        args = []
        for arg in rnod:
            name, dtype = self.split(arg, ":")
            dtype = self.visit_type(dtype)
            args += [[name[0], dtype]]
        return args.copy()

    def visit_type(self, rnod):
        return "".join(tuple(rnod))

    def enter(self, scope):
        self.state += "~%s" % scope

    def split(self, arr, sep):
        ret = [[]]
        pos = 0
        for i in arr:
            if i == sep:
                ret += [[]]
                continue
            ret[-1] += [i]
        return ret.copy()

    def exit(self):
        self.state = self.state. \
            removesuffix('~'+self.state. \
            split('~')[-1])

    def extract(self, arr, beg, end):
        ret = []
        BODY = 0
        for i in arr:
            if i == beg:
                BODY = 1
                continue
            if i == end:
                break
            if BODY:
                ret += [i]
        return ret.copy()


FORMAT = {
    "mbr": "binary",
    "exe_gui": f"PE GUI 4.0\n\ninclude '{home}/.local/lib/honey1.1/asm/WIN%sA.INC'",
    "exe": f"PE\n\ninclude '{home}/.local/lib/honey1.1/asm/WIN%sA.INC'",
    "exe_con": f"PE console\n\ninclude '{home}/.local/lib/honey1.1/asm/WIN%sA.INC'",
    "elf": "ELF executable 3",
    "so": "ELF linkable 3",
    "macho": "binary",
    "dll": f"PE DLL\n\ninclude '{home}/.local/lib/honey1.1/asm/WIN%sA.INC'",
    "efi": "EFI",
    "uefi": "EFI",
    "bin": "binary",
    "sys": "PE native"
}

WORD = {
    "8": "byte",
    "16": "word",
    "24": "hword",
    "32": "dword",
    "64": "qword"
}

REG = {
    "ax": {
        "byte": "al",
        "word": "ax",
        "dword": "eax",
        "qword": "rax"
    },
    "sp": {
        "byte": "NOREG",
        "word": "sp",
        "dword": "esp",
        "qword": "rsp"
    }
}

START = {
    "mbr.x86_16": \
    """_start:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov gs, ax
    mov fs, ax
    mov ss, ax
    mov ax, 0x7C00
    add ax, !STACK_SIZE
    mov sp, ax
    mov ax, 3
    int 0x10
    xor ax, ax
    call main$$main
    hlt
    ret
""",
    "exe.x86_32": \
    """_start:
    xor eax, eax
    mov esp, 0xFFFFFFFF-!STACK_SIZE
    call main$$main
    invoke ExitProcess,0
""",
    "elf.x86_32": \
    """_start:
    call main$$main
    mov eax, 1
    xor ebx, ebx
    int 0x80
"""
}

END = {
    "mbr.x86_16": \
    """times 510-$+$$ db 0x00
dw 0xAA55
""",
    "exe.x86_32": \
    """!section \".idata\" data import readable
    library KERNEL32, 'KERNEL32.DLL',\\
        USER32, 'USER32.DLL'

    import KERNEL32,\\
        ExitProcess, 'ExitProcess'

    import USER32,\\
        MessageBox, 'MessageBoxA'
"""
}


class Asm:
    parser: Parser

    def __init__(self, parser):
        self.parser = parser

        self.code = ""

        self.handle_metadata()
        self.handle_using()
        self.handle_code()
        self.handle_data()
        self.handle_end()

    def handle_end(self):
        self.code += "\n\n%s\n" % END[self.format()]

    def handle_metadata(self):
        self.code += "format "+FORMAT[self.parser.format].replace(f"%s", self.parser.bits)+"\n"
        self.code += "use"+self.parser.bits+"\n\n"
        self.code += "include \"%s/.local/lib/honey1.1/hna/%s/macros.asm\"\n\n" % (home, self.format())
        self.code += "!org %s\n\n" % self.parser.base
        self.code += "!entry _start\n\n"
        self.code += "!STACK_SIZE fix %s\n\n" % self.parser.stack

    def handle_using(self):
        for use in self.parser.using:
            self.code += "include \"%s/.local/lib/honey1.1/hna/%s/%s.asm\"\n" % (home, use, self.format())
        self.code += "\n"

    def handle_code(self):
        self.code += "!section \".code\" code readable executable\n"

        self.code += "\n%s\n" % START[self.format()]

        for proc in self.parser.procs:
            name, args, body = proc

            self.code += "%s$%s$%s:\n" % (
                self.parser.pkg,
                "",
                name
            )

            self.handle_body(body)

        for u in self.parser.using:
            self.add("\n%s!code\n" % u)

    def handle_body(self, body):
        for ln in body:
            cmd, prm = ln
            wrd = WORD[self.parser.bits]

            ax = REG["ax"][wrd]

            sp = REG["sp"][wrd]

            if cmd == "LOD":
                self.add("mov %s %s, [%s]" % (wrd, ax, prm))

            if cmd == "SVF":
                self.add("!%s!SVF" % prm)

            if cmd == "SVD":
                self.add("mov %s [%s], %s" % (wrd, prm, ax))

            if cmd == "CAL":
                self.add("call %s" % prm)

            if cmd == "CLS":
                if prm == "STACK":
                    self.add("mov %s, !STACK_SIZE" % sp)

            if cmd == "RET":
                self.add("ret")

    def handle_data(self):
        self.code += "\n!section \".rodata\" data readable\n\n"
        for n, c in enumerate(self.parser.consts):
            self.add("%s %s %s" % (
                "CONST!%s!%d" % (c[0], n),
                c[0],
                c[1]
            ))
        for u in self.parser.using:
            self.add("\n    %s!rodata\n" % u)
        self.code += "\n!section \".data\" data readable writable\n\n"
        for p in self.parser.procs:
            for n, a in enumerate(p[1]):
                self.add("%s %s %s" % (
                    "ARG!%s!%s:\n    ARG!%s!%s" % (p[0], n, p[0], a[0]),
                    a[1]+"!init",
                    "NULL"
                ))
        for u in self.parser.using:
            self.add("\n    %s!data\n" % u)

    def add(self, *ln):
        for l in ln:
            self.code += "    %s\n" % l

    def format(self):
        return "%s.%s_%s" % (
            self.parser.format,
            self.parser.arch,
            self.parser.bits
        )


lexer = Lexer(code)
parser = Parser(lexer)

if DEBUG:
    pdict = {**parser.__dict__}
    del pdict["lexer"]
    print("Parsed data:")
    pprint(pdict)
    print()

asm = Asm(parser)

if DEBUG:
    print("Generated asm code:")
    print("    "+asm.code.replace("\n", "\n    "))
    print()

with open("%s.asm" % outfile, "wt") as f:
    f.write(asm.code)

if "--asm" not in sys.argv:
    os.system(home+"/.local/bin/hny_asm_%s-%s %s.asm" % (parser.arch, parser.bits, outfile))
    os.unlink("%s.asm" % outfile)
