# Dependencies

This application is implemented in Python 2.7 and needs the following
libraries to be installed:

* NumPy
* SciPy
* NiBabel
* Matplotlib
* PyQt5

If you get problems with matplotlib while running the test-config.py, install python-tk (TKinter) for Linux and ActiveTcl for Mac OS X.

# Configuration help

In order to test the configuration, run the following command:

~~~
python scripts/test-config.py
~~~

# Running the program

First ensure that the UI-files are compiled to Python-files by
running:

~~~
make
~~~

Then run the main python file with the following command:

~~~
python main.py
~~~

# Build standalone application

Specific libraries required:

* pyinstaller
* pyobjc-framework-Cocoa (Mac Only)

To build the application run:

~~~
make dist
~~~

