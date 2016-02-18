# Configuration help

In order to install SPM12, run the following command:

~~~
./scripts/download-spm.bash
~~~

In order to test the configuration, run the following command:

~~~
python scripts/test-config.py
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
