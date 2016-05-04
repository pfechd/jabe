#!/bin/bash

cd ~/guitest/projekt
source ~/guitest/bin/activate
git pull
make
python main.py
