% How various formats can deal with LaTeX math
% HPL
% Aug 11, 2013

This document is translated to the format _pandoc_. The purpose is to
test math and doconce and various output formats.

*Test 1: Inline math.* Here is a sentence contains the equation $u(t)=e^{-at}$.

*Test 2: A single equation without label.* Here it is

$$
 u(t)=e^{-at} 
$$

*Test 3: A single equation with label.* Here it is as a one-line
latex code,


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!bt
\begin{equation} u(t)=e^{-at} \label{eq1}\end{equation}
!et
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

looking like

$$
\begin{equation} u(t)=e^{-at} \label{eq1}\end{equation}
$$
and as a three-line latex code:


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!bt
\begin{equation}
u(t)=e^{-at} \label{eq1b}
\end{equation}
!et
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

looking like

$$
\begin{equation}
u(t)=e^{-at} \label{eq1b}
\end{equation}
$$
This equation has label \eqref{eq1b}.


*Test 4: Multiple, aligned equations without label.* Only the align
environment is supported by other formats than LaTeX for typesetting
multiple, aligned equations. The code reads


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!bt
\begin{align*}
u(t)&=e^{-at}\\ 
v(t) - 1 &= \frac{du}{dt}
\end{align*}
!et
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

and results in

$$

u(t)=e^{-at}

$$

$$
  
v(t) - 1 = \frac{du}{dt}

$$

*Test 5: Multiple, aligned equations with label.* We use align with
labels:


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!bt
\begin{align}
u(t)&=e^{-at}
\label{eq2b}\\ 
v(t) - 1 &= \frac{du}{dt}
\label{eq3b}
\end{align}
!et
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

and results in

$$
\begin{equation}
u(t)=e^{-at} \label{eq2b}
\end{equation}
$$

$$
\begin{equation}  
v(t) - 1 = \frac{du}{dt} \label{eq3b}
\end{equation}
$$
We can refer to the last equations as the system \eqref{eq2b}-\eqref{eq3b}.


Original Pandoc-extended Markdown transformed to HTML via Pandoc
does not work with labels and multiple equations. `doconce md2html`
fixes the trouble by adding full support for MathJax and avoiding
that eqref references become empty.

One can write with align and labels in the Doconce document and get excellent
output in LaTeX, HTML, Sphinx, and Markdown-based HTML. Without
`doconce md2html` one must accept that labeles have very limited support
compared to more advanced MathJax.


*Test 6: Multiple, aligned eqnarray equations without label.* Let us
try the old eqnarray environment.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!bt
\begin{eqnarray*}
u(t)&=& e^{-at}\\ 
v(t) - 1 &=& \frac{du}{dt}
\end{eqnarray*}
!et
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

and results in

$$
\begin{eqnarray*}
u(t)&=& e^{-at}\\ 
v(t) - 1 &=& \frac{du}{dt}
\end{eqnarray*}
$$

*Test 7: Multiple, eqnarrayed equations with label.* We use eqnarray with
labels:


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
!bt
\begin{eqnarray}
u(t)&=& e^{-at}
\label{eq2c}\\ 
v(t) - 1 &=& \frac{du}{dt}
\label{eq3c}
\end{eqnarray}
!et
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

and results in

$$
\begin{eqnarray}
u(t)&=& e^{-at} \label{eq2c}\\ 
v(t) - 1 &=& \frac{du}{dt} \label{eq3c}
\end{eqnarray}
$$
Can we refer to the last equations as the system \eqref{eq2c}-\eqref{eq3c}?

*Test 8: newcommands and boldface bm vs pmb.* We have

$$
 \color{blue}{\frac{\partial\u}{\partial t}} +
\nabla\cdot\nabla\u = \nu\nabla^2\u -
\frac{1}{\varrho}\nabla p,
$$
and $\nabla\u (\pmb{x})\cdot\pmb{n}$
with plain old pmb. Here are the same formulas using `\bm`:

$$
 \color{blue}{\frac{\partial\ubm}{\partial t}} +
\nabla\cdot\nabla\ubm = \nu\nabla^2\ubm -
\frac{1}{\varrho}\nabla p,
$$
and $\nabla\ubm (\xbm)\cdot\normalvecbm$.

Note: for the pandoc format, `\bm` was substituted by Doconce
to `\boldsymbol`.

