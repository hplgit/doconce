from __future__ import print_function
import sympy as sm
x, y, a = sm.symbols('x y a')
f = a*x + y**2*sm.sin(y)
step1 = sm.Integral(f, x, y)
print(step1)
step2 = sm.Integral(sm.Integral(f, x).doit(), y)
print(step2)
step3 = step2.doit()
print(step3)

