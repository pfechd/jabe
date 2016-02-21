#!/bin/env python

# Creates a shared persistent MATLAB session which decreases the
# startup-time of the application.

import matlab.engine

e = matlab.engine.connect_matlab()
e.cd("src/matlab")

print "Ready!"

input()
