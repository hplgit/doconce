from __future__ import division
from __future__ import print_function
from past.utils import old_div
def f(x):
    """Runge's function."""
    return old_div(1,(1 + x**2))

# Plot f
import matplotlib.pyplot as plt
import numpy as np
xcoor = np.linspace(-3, 3, 101)
ycoor = f(xcoor)
plt.plot(xcoor, ycoor)
plt.savefig('f_plot.png')

# Compute f'(x) symbolically and make a Python function out of it
import sympy as sm
x = sm.Symbol('x')
f_expr = f(x)
print(f_expr)
df_expr = sm.diff(f_expr, x)
print(df_expr)
df = sm.lambdify(x, df_expr)  # turn expression into Python function

# Plot f'(x)
plt.figure()
plt.plot(xcoor, df(xcoor))
plt.savefig('df_plot.png')
plt.show()


