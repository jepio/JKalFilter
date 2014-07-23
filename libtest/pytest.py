#!/usr/bin/python
from ctypes import CDLL, c_int, POINTER
import numpy as np
from random import random
from time import time


# Load library
libName = "libtest.so"
libc = CDLL(libName)
libc.main()

# Create data set
gen_array = libc.gen_array
gen_array.restype = POINTER(c_int)

N = 1000000
start = time()
ptr = gen_array(N)
stop = time()
print 'gen array',stop-start,'s'
start = time()
py_table = [ptr[i] for i in xrange(N)]
stop = time()
print 'py table',stop-start,'s'
size = N

""" Old, slow, Python way
start = time()
py_table = [int(random() * N) for i in xrange(N)]
size = len(py_table)
stop = time()
print 'Gen random', stop - start, 'seconds'
"""

""" Very slow
c_table = c_int * size
start = time()
c_table_instance = c_table(*py_table)
stop = time()
print 'Create C array', stop - start, 'seconds'
"""

start = time()
cavg = libc.average(ptr, size)
stop = time()
print cavg
print 'C took:', stop - start, 'seconds'

start = time()
total = sum(py_table)
total /= size
stop = time()
print total
print 'Py took:', stop - start, 'seconds'

arr = np.array(py_table)
start = time()
average = np.mean(arr)
stop = time()
print average
print 'Numpy took:', stop - start, 'seconds'

