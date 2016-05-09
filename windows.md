# Download

The following links are to libraries which works together, every
package is necessary for running the application. Put all the
downloaded files in one directory together with the application.

* NumPy and SciPy from http://www.lfd.uci.edu/~gohlke/pythonlibs/
* pip from https://bootstrap.pypa.io/get-pip.py
* git from https://git-scm.com/download/win

# Installing

Install pip by running the following lines in Powershell:

~~~
python get-pip.py
~~~

Install NumPy and SciPy using pip (update the file names if necessary):

~~~
pip install .\numpy-1.10.4+mkl-cp27-cp27m-win_amd64.whl .\scipy-0.17.0-cp27-none-win_amd64.whl
~~~

Install PyQt5 using pip:

~~~
pip install git+git://github.com/pyqt/python-qt5.git
~~~

Install nibabel and matplotlib using pip:

~~~
pip install nibabel matplotlib
~~~

Ask a friend which uses Mac OS X or Linux to provide your with the .py
files in the folder "generated_ui" after they have run the command
`make`. Put these files in the "generated_ui" folder.

Finally, run the application by typing

~~~
python main.py
~~~

