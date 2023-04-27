def is_string(d):
	return d.strip()[0] == '"' and d.strip()[-1] == '"'

def to_string(d):
	return '<%s>' % d.replace("\\n", '", 0x0D, 0x0A, "')#.\
	#	replace("\\r", '", 0x0D, "').replace("\\v", '", 0x0A, "').\
	#	replace('\"', '""')

def get_const(t, n):
	return "CONST!%s!%d" % (t, n)