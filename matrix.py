"""
A module implementing the Matrix class.
Based on:
https://github.com/ozzloy/udacity-cs373/blob/master/unit-2.py
"""
# pylint: disable=W0141,C0103


class Matrix(object):

    """
    A matrix class covering all major matrix operations. Currently the
    operations +, - and * are supported. Matrix elements can also be accessed
    and modified using indexing.

    A matrix is constructed in one of two ways: passing a list of lists to the
    constructor or creating an :py:meth:`identity`/:py:meth:`zero` matrix and
    modifying the elements. If the constructor is invoked without parameters an empty matrix will be initialized from the list [[]].

        >>> A = Matrix([[1,2,3],[4,5,6]])
        >>> A
        Matrix([[  1.00,  2.00,  3.00],
                [  4.00,  5.00,  6.00]])
        >>> A[1][1]
        5
        >>> A[1][1] = 0.0
        >>> A
        Matrix([[  1.00,  2.00,  3.00],
                [  4.00,  0.00,  6.00]])

    Once a row has been accessed, the columns of that row can be sliced and
    modified.

        >>> A[1][:] = [5, 5, 5]
        Matrix([[  1.00,  2.00,  3.00],
                [  5.00,  5.00,  5.00]])

    By accessing the :py:attr:`I` or :py:attr:`T` fields the
    inverse/transposed matrix can be retrieved accordingly. An existing matrix
    may be modified by assigning a list of lists to the :py:attr:`value` field.

        >>> A.value = [[1, 1],[-1, 1]]
        >>> A
        Matrix([[  1.00,  1.00],
                [ -1.00,  1.00]])
        >>> A * A.I
        Matrix([[  1.00,  0.00],
                [  0.00,  1.00]])

    """

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
        self._T = None
        self._I = None

    ################# Properties available externally ##################
    @property
    def value(self):
        """ Get underlying matrix value, that is a list of list. """
        # Can't be sure if the user uses this to change a matrix entry so have
        # to reset existing cached inverse and transpose.
        self._T = None
        self._I = None
        return self._value

    @value.setter
    def value(self, value):
        """ Set matrix value. """
        self.dimx = len(value)
        self.dimy = len(value[0])
        self._value = value
        self._T = None
        self._I = None

    @property
    def T(self):
        """
        Get transposed matrix. The result is cached so that subsequent
        accesses to the transposed matrix are instantaneous. The result is
        uncached if the user accesses the matrix :py:attr:`.value` or a matrix
        element through indexing.
        """
        if self._T is None:
            self._T = self._transpose()
        return self._T

    ##################### Spawning special matrices ####################
    @classmethod
    def zero(cls, dimx, dimy):
        """ Return a zero matrix of size *dimx* x *dimy*. """
        if dimx < 1 or dimy < 1:
            raise ValueError("Invalid size of matrix")
        else:
            value = [[0 for _ in range(dimy)] for _ in range(dimx)]
            return cls(value)

    @classmethod
    def identity(cls, dim):
        """ Return an identity matrix of size *dim* x *dim*. """
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

        # formatting function
        def format_row(row):
            row = ["{:6.2f}".format(i) for i in row]
            row = ','.join(row)
            return '[' + row + ']'

        return name + join_string.join(map(format_row, self._value)) + "])"

    def __str__(self):
        """ Return the printed version of matrix. """
        return '[' + ",\n ".join(map(str, self._value)) + ']'

    def size(self):
        """
        Return shape of matrix as a tuple (*dimx*, *dimy*).
        """
        return (self.dimx, self.dimy)

    def __getitem__(self, k):
        """ Return row of matrix. """
        return self.value[k]

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
        Return the LU decomposition of matrix, that is matrices :math:`L` and
        :math:`U` such that :math:`LU = \text{self}`. Uses the Crout
        decomposition method, described at
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
                    L[i][i] = 1e-20
                U[i][j] = (self[i][j] - tot) / L[i][i]
        return (L, U)

    @staticmethod
    def LUInvert(L, U):
        """
        Return the inverse matrix of :math:`A = LU` where :math:`L, U`
        are the LU decomposition matrices.

        The method works by looking at the solution to the system

        .. math::
            LU \\cdot X = B

        column by column (uncapitalized letters symbolize column vectors,
        capitals represent the matrix of column vectors).
        :math:`B` is :math:`\\mathbb{1}` - the identity matrix.
        First

        .. math::
            L \\cdot y = b

        is solved, then

        .. math::
            U \\cdot x = y

        The inverse matrix is then :math:`X`, the matrix of column vectors
        :math:`x`. Since :math:`L` and :math:`U` are both triangular matrices,
        the solution of these systems can be found through simple gaussian
        elimination.
        """

        dim, _ = L.size()
        inverted = Matrix.zero(dim, dim)
        # unit = Matrix.identity(dim)
        # Upper elimination
        try:
            for i in range(dim):
                col_y = [0 for _ in range(dim)]

                # The j'th row of the i'th column in an identity matrix will be
                # the first one with a one
                col_y[i] = 1.0 / L[i][i]
                for j in range(i + 1, dim):
                    rest = sum(l * y for y, l in zip(col_y[i:j], L[j][i:j]))
                    col_y[j] = -rest / L[j][j]
                col_x = [0 for _ in range(dim)]
                for j in reversed(range(dim)):
                    rest = sum(
                        u * x for x, u in zip(col_x[j:dim], U[j][j:dim]))
                    col_x[j] = (col_y[j] - rest) / U[j][j]
                    inverted[j][i] = col_x[j]
                # inverted[i] = col_y # <-- needs a __set_item__ method
            return inverted
        except ZeroDivisionError:
            print "Matrix is not invertible"
            return None

    def _inverse(self):
        """ Return the inverse matrix. """
        L, U = self.LU()
        new = Matrix.LUInvert(L, U)
        return new

    @property
    def I(self):
        """
        Get inverse matrix through LU decomposition. The result is cached so
        that subsequent accesses to the inverse matrix are instantaneous. The
        result is uncached if the user accesses the matrix :py:attr:`.value`
        or a matrix element through indexing.
        """
        if self._I is None:
            self._I = self._inverse()
        return self._I
