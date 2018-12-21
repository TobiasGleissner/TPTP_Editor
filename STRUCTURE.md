* `bin/`
  Will contain all binaries created by the build process
  - run_webapp
  Starts the editor
  - run_>tool<
  Starts the corresponding tool as standalone application

* `build`
  Will contain all repositories cloned during the build process and additional files created during the build process. Cloned Repositories:
  - antlr4 \
    ANTLR4 parser generator sources
  - embed_modal \
    A java library for embedding non-classical logics formulated in TPTP THF into classical higher-order logic formulated in TPTP THF
  - fancytree \
    A javascript tree library
  - jstree \
    A javascript tree library
  - tptp_antlr_grammar \
    The ANTLR4 grammar for the TPTP
  - tptp_tools \
    A python library for manipulating TPTP input, accessing remote TPTP tools

* `contrib/`
  Contains all external contributed source code. The build process will clone external projects into this directory
  - TreeLimitedRun
    A wrapper for running binaries and killing all associated (sub-)processes after a defined timeout

* `webapp/`
  Contains all core code for the editor software

* `build.py`
  Entry point of the build process, used as described in README.md
* `README.md`
  Project description and install guide
* `STRUCTURE.md`
  This file  

