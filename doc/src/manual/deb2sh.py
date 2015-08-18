"""
Read a text file specifying Debian packages to be installed.
Generate a shell script and a Python script for performing
each install command separately with check of success/failure
and abortion in case of failure.

File syntax:

 * # Comment lines are just output to the shell script.
 * Spaces are ignored.
 * Lines starting with $ are plain Unix commands copied to the script.
 * Other lines specify the names of Debian packages to be installed
   by sudo apt-get install packagename.

"""
import sys
try:
    debpkg = sys.argv[1]
except IndexError:
    debpkg = 'debpkg.txt'

f = open(debpkg, 'r')
lines = f.readlines()
f.close()
outfile = debpkg[:-4].replace('debpkg', 'install')
shfile = open(outfile + '.sh', 'w')
cmd = 'sudo apt-get update --fix-missing'
shfile.write("""\
#!/bin/bash
# Automatically generated script by deb2sh.py.

# The script is based on packages listed in %s.

set -x  # make sure each command is printed in the terminal

function apt_install {
  sudo apt-get -y install $1
  if [ $? -ne 0 ]; then
    echo "could not install $1 - abort"
    exit 1
  fi
}

function pip_install {
  sudo pip install --upgrade "$@"
  if [ $? -ne 0 ]; then
    echo "could not install $p - abort"
    exit 1
  fi
}

%s

""" % (debpkg, cmd))

pyfile = open(outfile + '.py', 'w')
pyfile.write(r'''#!/usr/bin/env python
# Automatically generated script by
# vagrantbox/doc/src/vagrant/src-vagrant/deb2sh.py
# where vagrantbox is the directory arising from
# git clone git@github.com:hplgit/vagrantbox.git

# The script is based on packages listed in %s.

logfile = 'tmp_output.log'  # store all output of all operating system commands
f = open(logfile, 'w'); f.close()  # touch logfile so it can be appended

import subprocess, sys

def system(cmd):
    """Run system command cmd."""
    print cmd
    try:
        output = subprocess.check_output(cmd, shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print 'Command\n  %%s\nfailed.' %% cmd
        print 'Return code:', e.returncode
        print e.output
        sys.exit(1)
    print output
    f = open(logfile, 'a'); f.write(output); f.close()

system('%s')
''' % (debpkg, cmd))

unix_commands = []

def run_unix_commands():
    """Run all everything on the stack unix_commands as a script."""
    global unix_commands
    cmd = '\n'.join(unix_commands)
    pyfile.write('''cmd = """
%s
"""
system(cmd)
''' % cmd)
    unix_commands = []


for line in lines:
    if line.strip() == '':
        shfile.write(line)
        pyfile.write(line)
        continue
    # Copy comment lines verbatim
    if line.startswith('#'):
        shfile.write(line)
        if unix_commands:
            unix_commands.append(line)
        else:
            pyfile.write(line)
        continue
    # Strip off comments at the end of the line:
    if '#' in line:
        line = line.split(' # ')[0]

    # Treat lines starting with $ as normal Unix commands
    if line.startswith('$'):
        cmd = line[1:].strip()
        shfile.write(cmd + '\n')
        unix_commands.append(cmd)
        continue

    # All other lines are supposed to list either pip install
    # packages or Debian package
    if 'pip install' in line:
        if line.startswith('$'):
            line = ' '.join(line.split()[1:])  # get rid of (wrong) $ prefix
        cmd = 'pip_install ' + ' '.join(line.split()[2:])
        shfile.write(cmd + '\n')
        if unix_commands:
            run_unix_commands()  # empty stack of previous unix commands
        cmd = 'sudo ' + line.strip()
        pyfile.write("system('%s')\n" % cmd)
    else:
        # Debian package names
        if unix_commands:
            run_unix_commands()  # empty stack and get ready for apt-get
        packages = line.split()
        for package in packages:
            shfile.write('apt_install ' + package + '\n')
            cmd = 'sudo apt-get -y install ' + package
            pyfile.write("system('%s')\n" % cmd)

shfile.write('echo "Everything is successfully installed!"\n')
shfile.close()
pyfile.write("print 'Everything is successfully installed!'\n")
pyfile.close()
print 'Generated %s.sh and %s.py with all install commands.' % \
      (outfile, outfile)
