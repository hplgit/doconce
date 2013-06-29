import re, sys, shutil
filename = sys.argv[1]
f = open(filename, 'r')
text = f.read()
f.close()

def subst1(m):
    opt = m.group(1)
    if opt != 'from':
        opt = opt.replace('-', '_')
    return ' --' + opt + m.group(2)

pattern1 = r' --([A-Za-z-]+)([= \n])'
text = re.sub(pattern1, subst1, text)

def subst2(m):
    opt = m.group(1)
    opt = opt.replace('-', '_')
    return 'option(' + opt + ')'

pattern2 = r"""option\((.+?)\)"""
text = re.sub(pattern2, subst2, text)

shutil.copy(filename, filename + '.old~~')
f = open(filename, 'w')
f.write(text)
f.close()
print 'treated', filename


