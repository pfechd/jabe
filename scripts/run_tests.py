#!/bin/env python

# Creates a shared persistent MATLAB session which decreases the
# startup-time of the application.

import os
import subprocess

pwd = os.getcwd()

print
print '=' * 25
print '#' + ' '*5 + 'RUNNING TESTS' + ' '*5 + '#'
print '=' * 25
print

t = subprocess.Popen(['python', '-m', 'unittest', 'discover', '-v', '-s', pwd + '/src/python/tests', '-p', 'test_*'])

t.wait()

print # Prettier output

#e.quit()