# A TPTP Editor

## Prerequisites
* Python 3.3 or higher
* Pip
* Java 8 or higher
* Maven 3 or higher
* GCC
* Git

## Installation
1. Get the repository by invoking
2. Ensure prerequisites are met and invoke
3. Clone external repositories with build.py
```
python3 build.py clone
```
4. Compile project with build.py
```
python3 build.py compile
```

## Reinstallation
To clean up the compiled files use
```
python3 build.py clean_compile
```
whis will not remove the cloned directories in the build directory

To clean up the cloned external repositories use
```
python3 build.py clean_clone
```


