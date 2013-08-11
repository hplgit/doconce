.. Automatically generated reST file from Doconce source
   (https://github.com/hplgit/doconce/)

How various formats can deal with LaTeX math
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: HPL
:Date: Aug 11, 2013

This document is translated to the format **sphinx**. The purpose is to
test math and doconce and various output formats.

*Test 1: Inline math.* Here is a sentence contains the equation :math:`u(t)=e^{-at}`.

*Test 2: A single equation without label.* Here it is


.. math::
         u(t)=e^{-at} 


*Test 3: A single equation with label.* Here it is as a one-line
latex code,


.. code-block:: text


        !bt
        \begin{equation} u(t)=e^{-at} label{eq1}\end{equation}
        !et

looking like


.. math::
   :label: eq1
         u(t)=e^{-at} 

and as a three-line latex code:


.. code-block:: text


        !bt
        \begin{equation}
        u(t)=e^{-at} label{eq1b}
        \end{equation}
        !et

looking like


.. math::
   :label: eq1b
        
        u(t)=e^{-at} 
        

This equation has label :eq:`eq1b`.


*Test 4: Multiple, aligned equations without label.* Only the align
environment is supported by other formats than LaTeX for typesetting
multiple, aligned equations. The code reads


.. code-block:: text


        !bt
        \begin{align*}
        u(t)&=e^{-at}\\ 
        v(t) - 1 &= \frac{du}{dt}
        \end{align*}
        !et

and results in


.. math::
        
        u(t)&=e^{-at}\\ 
        v(t) - 1 &= \frac{du}{dt}
        


*Test 5: Multiple, aligned equations with label.* We use align with
labels:


.. code-block:: text


        !bt
        \begin{align}
        u(t)&=e^{-at}
        label{eq2b}\\ 
        v(t) - 1 &= \frac{du}{dt}
        label{eq3b}
        \end{align}
        !et

and results in


.. math::
   :label: eq2b
        
        u(t)=e^{-at} 
        



.. math::
   :label: eq3b
          
        v(t) - 1 = \frac{du}{dt} 
        

We can refer to the last equations as the system :eq:`eq2b`-:eq:`eq3b`.

Actually, *Sphinx does not support the align environment with labels*,
such as we write above,
but Doconce splits in this case the equations into separate, single equations
with labels. Hence the user can write one code with align and labels
and have to work in LaTeX, HTML, and Sphinx. The generated Sphinx code
in the present case is


.. code-block:: rst

        .. math::
           :label: eq2b
        
                u(t)=e^{-at}
        
        
        .. math::
           :label: eq3b
        
                v(t) - 1 = \frac{du}{dt}
        




*Test 6: Multiple, aligned eqnarray equations without label.* Let us
try the old eqnarray environment.


.. code-block:: text


        !bt
        \begin{eqnarray*}
        u(t)&=& e^{-at}\\ 
        v(t) - 1 &=& \frac{du}{dt}
        \end{eqnarray*}
        !et

and results in


.. math::
        
        u(t) &=  e^{-at}\\ 
        v(t) - 1  &=  \frac{du}{dt}
        


*Test 7: Multiple, eqnarrayed equations with label.* We use eqnarray with
labels:


.. code-block:: text


        !bt
        \begin{eqnarray}
        u(t)&=& e^{-at}
        label{eq2c}\\ 
        v(t) - 1 &=& \frac{du}{dt}
        label{eq3c}
        \end{eqnarray}
        !et

and results in


.. math::
        
        u(t) &=  e^{-at} \\ 
        v(t) - 1  &=  \frac{du}{dt} 
        

Can we refer to the last equations as the system :eq:`eq2c`-:eq:`eq3c`?
No, unfortunately not.
Note: Doconce takes the eqnarray with labels and replaces it automatically
by the Sphinx code


.. code-block:: rst

        .. math::
        
                u(t) &=  e^{-at} \\ 
                v(t)  &=  \frac{du}{dt}

That is why the equation numbers are gone and that eqnarray seemingly
works. MathJax does not support eqnarray with labels so Sphinx would
probably fail to show them (unless one tries PNG images or other
math engines?). The rule of thumb is to avoid equarray.

*Test 8: newcommands and boldface bm vs pmb.* We have


.. math::
         \color{blue}{\frac{\partial\pmb{u}}{\partial t}} +
        \nabla\cdot\nabla\pmb{u} = \nu\nabla^2\pmb{u} -
        \frac{1}{\varrho}\nabla p,

and :math:`\nabla\pmb{u} (\pmb{x})\cdot\pmb{n}`
with plain old pmb. Here are the same formulas using ``\bm``:


.. math::
         \color{blue}{\frac{\partial\boldsymbol{u}}{\partial t}} +
        \nabla\cdot\nabla\boldsymbol{u} = \nu\nabla^2\boldsymbol{u} -
        \frac{1}{\varrho}\nabla p,

and :math:`\nabla\boldsymbol{u} (\boldsymbol{x})\cdot\boldsymbol{n}`.

Note: for the sphinx format, ``\bm`` was substituted by Doconce
to ``\boldsymbol``.
