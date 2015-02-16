from ctypes import cdll, c_int, POINTER
import os

PATH = os.path.dirname(os.path.realpath(__file__))
_libtest = cdll.LoadLibrary(os.path.join(PATH, "_libtest.so"))

_c_int_ptr = POINTER(c_int)

gen_array = _libtest.gen_array
gen_array.argtypes = [c_int]
gen_array.restype = _c_int_ptr

average = _libtest.average
average.argtypes = [_c_int_ptr, c_int]
average.restype = c_int

