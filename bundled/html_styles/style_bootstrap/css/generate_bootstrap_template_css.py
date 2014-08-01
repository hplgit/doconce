import sys, shutil
template_name = sys.argv[1]
shutil.copy('bootstrap_template.css', 'bootstrap_%s.css' % name)
f = open('bootstrap_%s.css' % name, 'r')
text = f.read()
f.close()

colors = '5B4634 82634A 9B7759 A88160 E8B285'.split()

NOT FINISHED...

# Use color scheme from http://kuler.adobe.com/
f = open('bootstrap_%s.css' % name, 'w')
f.write(text)
f.close()


