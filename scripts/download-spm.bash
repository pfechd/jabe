#!/bin/bash
# This script will download spm12.zip, unpack it to the current
# directory and then remove the zip-file again.

wget http://www.fil.ion.ucl.ac.uk/spm/download/restricted/eldorado/spm12.zip
unzip spm12.zip
rm spm12.zip
