JKalFilter
===========

A Kalman Filter library written in Python. This package should be viewed as a
modular framework consisting of 5 core modules:

1. *matrix* - a simple linear algebra module.
2. *kfilter* - linear Kalman Filters that can be iterated in one or two
   directions.
3. *detector* - a detector simulation module that implements different
   geometries that can respond to particles.
4. *track* - different types of physical tracks that can propagate inside the
   detector.
5. *fitter* - a module facilitating interaction between *kfilter* and
   *detector*

Aside from the core modules, tests exist that present the functionalities of
*matrix*, *kfilter*, *track* and *fitter*.

The whole package can be conveniently imported by using:
```python
from JKalFilter import *
```

Python version
--------------
This framework was only tested on Python 2.7.8. It will not work with Python 3
unaltered, however the required changes should not be significant.


Installation
-------------
The whole package can be installed using the command:
```bash
python setup.py install
```
from the main directory.


Tests
-----
All tests are located in `test/` subdirectories, and currently cannot be run
from the command line by executing `python test_<name>.py`, one must execute
them with the full package name from beyond the toplevel directory:
```bash
python -m JKalFilter.test.test_matrix
```
If anyone knows how to fix this, please open and issue and tell me.

If the test requires command line arguments the user will be informed of that.

1. `test_matrix.py` contains unit tests for all functions contained in the
   matrix module.
2. `test_filter.py` contains two tests of **LKFilter** used for filtering
   noise from a first and second degree polynomial. Number of iterations
   and function can be selected by passing appropriate command line arguments.
3. `test_track.py` contains a test of propagating tracks inside a detector.
   Needs *matplotlib*.
4. `test_fitting.py` contains a test of the fitting capabilities of the
   **FitManager**. Needs *matplotlib*.

The folder [libtest](./libtest) contains a simple example of using *ctypes* to
extend Python using C. Build with `make` and run `test_libtest.py` to see a
comparison of run times.

The test suites `test_filter`, `test_matrix` and `test_libtest` can all be run
automatically with `py.test`.

Documentation
-------------

Documentation is available at [github pages](https://jepio.github.com/JKalFilter).

