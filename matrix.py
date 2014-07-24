"""
A module implementing the Matrix class.
Based on:
https://github.com/ozzloy/udacity-cs373/blob/master/unit-2.py
"""
# pylint: disable=W0141,C0103


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
        # if value == [[]]:
        #    self.dimx = 0

    ################# Properties available externally ##################
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

    @property
    def T(self):
        """ Get transposed matrix. """
        return self._transpose()

    ##################### Spawning special matrices ####################
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

    ####################### Helper methods  ############################
    def show(self):
        """ Print the matrix. """
        for i in range(self.dimx):
            print self._value[i]
        print ' '

    def __repr__(self):
        """ Return string representation of matrix. """
        name = self.__class__.__name__ + "(["
        # class name and left bracket
        pad = len(name)
        join_string = ',\n' + ' ' * pad
        return name + join_string.join(map(str, self._value)) + "])"

    def __str__(self):
        """ Return the printed version of matrix. """
        return '[' + ",\n ".join(map(str, self._value)) + ']'

    def size(self):
        """ Return shape of matrix. """
        return (self.dimx, self.dimy)

    def __getitem__(self, k):
        """ Return row of matrix. """
        return self._value[k]

    def _transpose(self):
        """ Return a transpose of the matrix. """
        dimx, dimy = self.size()
        value = [[self[y][x] for y in range(dimx)] for x in range(dimy)]
        return Matrix(value)

    ############################ Arithmetics ###########################
    def __eq__(self, other):
        return self.value == other.value

    def __neq__(self, other):
        return self.value != other.value

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
        _, dimy1 = self.size()
        dimx2, _ = other.size()
        if dimy1 != dimx2:
            raise ValueError("Matrices do not have the proper dimensions")

        # Easier to handle transposed matrix - columns of original are then
        # lists
        other = other.T

        def func(row, col):
            """ Return the vector product for row v and col v. """
            # Row and column are the same length
            # Create a list of tuples containing entries
            zipped = zip(row, col)
            # Reduce the tuples using multiplication
            func = lambda tupl: tupl[0] * tupl[1]
            mult = sum(func(tupl) for tupl in zipped)
            return mult

        # other is transposed, so columns can be accessed as lists
        new = [[func(row, col) for col in other.value] for row in self.value]
        return Matrix(new)

    # Special functions
    def LU(self):
        """
        Return the LU decomposition of matrix, that is matrices L and U such
        that L*U = self. Uses the Crout decomposition method, described at
        http://en.wikipedia.org/wiki/Crout_matrix_decomposition

        The input matrix needs to be square.
        """
        dimx, dimy = self.size()
        if dimx != dimy:
            raise ValueError("Matrix is not square")
        dim = dimx
        L = Matrix.zero(dim, dim)
        U = Matrix.identity(dim)
        for i in range(dim):
            for j in range(i, dim):
                tot = 0.0
                for k in range(i):
                    tot += L[j][k] * U[k][i]
                L[j][i] = self[j][i] - tot
            for j in range(i, dim):
                tot = 0.0
                for k in range(i):
                    tot += L[i][k] * U[k][j]
                if L[i][i] == 0:
                    L[i][i] = 1e-40
                U[i][j] = (self[i][j] - tot) / L[i][i]
        return (L, U)
