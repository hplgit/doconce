#!/bin/sh
# Make html page with all figure files in this directory

rm -f display.html
touch display.html
for f in *.png *.gif *.jp*g; do
  echo "<img src=\"$f\" align=\"bottom\">$f\n<hr>\n" >> display.html
done
echo load display.html into a browser
