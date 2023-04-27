import os

cont = os.listdir('.')

for fil in cont:
    if fil.endswith('.py'):
        with open(fil, 'rt') as f:
            data = f.read().replace('\t', ' '*4)
        with open(fil, 'wt') as f:
            f.write(data)
#
