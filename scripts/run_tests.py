#!/bin/env python

# Creates a shared persistent MATLAB session which decreases the
# startup-time of the application.

import os
import subprocess
import sys
import matlab.engine

pwd = os.getcwd()
e = matlab.engine.connect_matlab()
e.cd("src/matlab")

print
print '=' * 25
print '#' + ' '*5 + 'RUNNING TESTS' + ' '*5 + '#'
print '=' * 25
print

if sys.version_info[0] != 2:
    t = subprocess.Popen(['python2.7', '-m', 'unittest', 'discover', '-v', '-s', pwd + '/src/python/tests', '-p', 'test_*'])
else:
    t = subprocess.Popen(['python', '-m', 'unittest', 'discover', '-v', '-s', pwd + '/src/python/tests', '-p', 'test_*'])

t.wait()

print # Prettier output

e.quit()