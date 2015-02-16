#!/usr/bin/python
import numpy as np
from time import time
from libtest import gen_array, average
from contextlib import contextmanager
import pytest


def test_wrong_param_count():
    with pytest.raises(TypeError):
        average()

def test_small_average():
    array = gen_array(5)
    for i in range(5):
        array[i] = i
    assert average(array, 5) == 2

N = 1000000

@contextmanager
def time_op(name):
    start = time()
    yield
    stop = time()
    print "%-15s: %7.4fs" % (name, stop - start)

with time_op("Gen array"):
    ptr = gen_array(N)

with time_op("Py table"):
    py_table = [ptr[i] for i in xrange(N)]

with time_op("C average"):
    cavg = average(ptr, N)
    print cavg

with time_op("Py average"):
    total = sum(py_table)
    total /= N
    print total

arr = np.array(py_table)
with time_op("Numpy average"):
    avg = int(np.mean(arr))
    print avg

