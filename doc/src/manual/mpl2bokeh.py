import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 2*np.pi, 1001)
y1 = np.exp(-x)*np.sin(2*x)
y2 = np.exp(-0.5*x)*np.sin(2*x)

plt.plot(x, y1, 'r-', x, y2, 'b--')
plt.xlabel('x');  plt.ylabel('y')
# legends do not work in Bokeh
#plt.legend([r'$e^{-x}\sin 2x$', r'$e^{-\frac{1}{2}x}\sin 2x$'])
plt.title('Damped sine functions')
plt.savefig('tmp.pdf');  plt.savefig('tmp.png')

# Convert to Bokeh
import bokeh.mpl, bokeh.plotting as bpl
p = bokeh.mpl.to_bokeh(notebook=False, xkcd=False)
#p = bokeh.mpl.to_bokeh()
bpl.output_file('tmp.html', mode='cdn')
bpl.save(p)
#bpl.show(p)

plt.show()
