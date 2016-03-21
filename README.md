# Dependencies

This application is implemented in Python 2.7 and needs the following
libraries to be installed:

* numpy
* scipy
* nibabel
* matplotlib
* PyQt5

If you get problems with matplotlib while running the test-config.py, install python-tk (TKinter) for Linux and ActiveTcl for Mac OS X.


# Configuration help

In order to install SPM12, run the following command:

~~~
./scripts/download-spm.bash
~~~

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

# Folder structure

The repository is structured as follows:

~~~
.
├── BOLDactivity1.m
├── main.py
├── makefile
├── README.md
├── scripts
│   ├── download-spm.bash
│   └── test-config.py
└── src
    ├── __init__.py
    ├── matlab
    │   └── hello_world.m
    ├── python
    │   ├── generated_ui
    │   │   └── __init__.py
    │   ├── gui.py
    │   ├── __init__.py
    │   └── session_manager.py
    └── ui
        └── hello_world.ui
~~~
