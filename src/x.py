def flat(a):
	r = []
	for i in a:
		if type(i) in (list, tuple):
			r += flat(i)
		else:
			r.append(i)
	return r.copy()

def split(a, s):
	r = [[]]
	for i in a:
		if i == s:
			r += [[]]
		else:
			r[-1] += [i]
	return r.copy()
