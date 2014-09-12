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

The whole package can be conveniently imported by using 
```python
from JKalFilter import *
```

The folder [libtest](./libtest) contains a simple example of using *ctypes* to
extend Python using C. Build with `make` and launch `./pytest.py` to see a
comparison of run times.

Documentation
-------------

Documentation is available at [github pages](https://jepio.github.com/JKalFilter).

