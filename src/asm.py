class Asm:
	def __init__(self):
		self.code = ""

	def build(self, data):
		self.oformat(data.oform)
		self.package(data.packg)
		self.using(data.using)
		self.funcs(data.funcs)
		self.const(data.const)

	def oformat(self, of):
		print(of)
		self.code += "\n!FORMAT "+of[0]+"\n"
		self.code += "!ARCH "+of[1]+"\n"
		self.code += "!BITS "+of[2]+"\n"
		self.code += "!ORG 0x7C00\n"
		self.code += "!STACK 1024\n"

	def package(self, pk):
		print(pk)
		self.code += "\n!PACKAGE "+pk+"\n"

	def using(self, us):
		print(us)
		self.code += "\n!USING\n"
		for u in us:
			self.code += "    "+u+"\n"
		self.code += "!END\n"

	def funcs(self, fns):
		print(fns)
		for fn in fns.values():
			name = fn[0]
			args = fn[1]
			body = fn[2]

			self.code += "\n!PROC "+name+"("+self.args(args)+")\n"
			for act in body:
				self.code += "    "+" ".join(tuple(str(i) for i in act))+"\n"
			self.code += "!END\n"

	def const(self, cs):
		self.code += "\n"
		for t in cs:
			for c in cs[t]:
				self.code += "!CONST (%s) %s\n" % (t, c)

	def args(self, args):
		r = ""
		for arg in args:
			r += ": ".join(tuple(arg))+", "
		return r[:-2]
