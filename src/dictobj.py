class Dictobj:
    dct = {}
    def __init__(self, **k):
        object.__setattr__(self, "dct", {**k})
        self.__class__ = object.__getattribute__(self, '__class__')
    
    def __getitem__(self, k):
        return object.__getattribute__(self, "dct")[k]
    
    def __setitem__(self, k, v):
        dct = object.__getattribute__(self, "dct")
        #print(dct)
        dct[k] = v
    
    def __getattribute__(self, k):
        return object.__getattribute__(self, "dct")[k]
    
    def __setattr__(self, k, v):
        dct = object.__getattribute__(self, "dct")
        #print(dct)
        dct[k] = v
    
    def __str__(self):
        #return str(list(object.__getattribute__(self, "dct").keys()))
        string = ""
        for k in object.__getattribute__(self, "dct").keys():
            if not k.startswith('__'):
                string += k+":\n"
                string += '    '+str(self[k]).replace("\n", "\n    ")+'\n'
        return string
    
    __repr__ = __str__
    