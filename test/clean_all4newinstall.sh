#!/bin/bash
echo "Clean everything with doconce to check installation"
echo "NOTE: The source is removed in reinstalled from hg!!"
echo "Don't run this script unless you are a Doconce developer"
echo "and you know very well what this script does!"

rm -f `which doconce2format`
rm -f `which doconce_insertdocstr`
prefix=`python -c 'import sys; print sys.prefix'`
pyver=`python -c 'import sys; print sys.version[:3]'`
rm -rf $prefix/lib/python$pyver/site-packages/doconce
rm -rf $prefix/lib/python$pyver/site-packages/Doconce*
cd ..
rm -rf build
hg commit -m 'ensure last changes are recorded'
hg push
echo 'if hg commit was successful, run these three commands manually:'
echo 'cd ..'
echo 'rm -rf lib bin'
echo 'hg pull; hg update'


