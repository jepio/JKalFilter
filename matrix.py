"""
A module implementing the Matrix class.
Based on:
https://github.com/ozzloy/udacity-cs373/blob/master/unit-2.py
"""
# pylint: disable=W0141

class Matrix(object):
    """ A matrix class covering all major matrix operations. """

    def __init__(self, value=None):
        """ Create a matrix from list of lists. """
        if value is None:
            value = [[]]
            self._value = value
            self.dimx = 0
            self.dimy = 0
        else:
            self._value = value
            self.dimx = len(value)
            self.dimy = len(value[0])
        #if value == [[]]:
        #    self.dimx = 0


    @property
    def value(self):
        """ Get matrix value. """
        return self._value
    @value.setter
    def value(self, value):
        """ Set matrix value. """
        self.dimx = len(value)
        self.dimy = len(value[0])
        self._value = value

    ## Spawning special matrices
    @classmethod
    def zero(cls, dimx, dimy):
        """ Return a zero matrix. """
        if dimx < 1 or dimy < 1:
            raise ValueError("Invalid size of matrix")
        else:
            value = [[0 for _ in range(dimy)] for _ in range(dimx)]
            return cls(value)

    @classmethod
    def identity(cls, dim):
        """ Return an identity matrix. """
        if dim < 1:
            raise ValueError("Invalid size of matrix")
        self = cls.zero(dim, dim)
        for i in range(dim):
            self.value[i][i] = 1
        return self


    def show(self):
        """ Print the matrix. """
        for i in range(self.dimx):
            print self._value[i]
        print ' '

    def __repr__(self):
        """ Return string representation of matrix. """
        return '\n'.join(map(str, self._value))

    def size(self):
        """ Return shape of matrix. """
        return (self.dimx, self.dimy)

    def __getitem__(self, k):
        """ Return row of matrix. """
        return self._value[k]

    ## Arithmetics
    def __add__(self, other):
        if self.size() != other.size():
            raise ValueError("Matrices are not the same size")
        dimx, dimy = self.size()
        new = [[self[x][y] + other[x][y] for y in range(dimy)] for x in
               range(dimx)]
        return Matrix(new)

    def __sub__(self, other):
        if self.size() != other.size():
            raise ValueError("Matrices are not the same size")
        dimx, dimy = self.size()
        new = [[self[x][y] - other[x][y] for y in range(dimy)] for x in
               range(dimx)]
        return Matrix(new)

    def __mul__(self, other):
        pass
