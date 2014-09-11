"""A Kalman Filter module. Currently two kinds of filters are implemented:

    1. a linear Kalman Filter (:py:class:`.LKFilter`)
    2. a linear Kalman Filter which can be updated both forward and backward
       (:py:class:`.TwoWayLKFilter`)
"""
# pylint: disable=C0103,R0192
from matrix import Matrix
import collections


class LKFilter(object):

    """
    A Linear Kalman Filter implementation. The filter needs to be initialized
    with the proper Kalman matrices (take care of proper dimensions) and a given
    valid estimates of initial state and covariance.

    Once initialized, the user has full control over what he does with the
    filter. If he so wishes, he can manually step it::

        >>> filt = LKFilter(A, H, x, P, Q, R)
        >>> for measurement in measurement_list:
        ...     estimate = filt.step(measurement)
        ...     # do something with estimate
        ...

    He can also iterate over a filter when it has measurements assigned to it::

        >>> filtered = []
        >>> filt.add_meas(measurement_list)
        >>> for estimate in filt:
        ...    # process estimate
        ...    filtered.append(estimate)

    If the user needs a more fine-grained control, he has access to the functions
    :py:meth:`.update` and :py:meth:`.predict`, the two basic building stones
    of a Kalman filter iteration. At any time the current state estimate of the filter can be accessed using the :py:attr:`.state` property.

    For more details on this implementation go to:
    http://greg.czerniak.info/guides/kalman1/
    """

    def __init__(self, A, H, x, P, Q, R):
        """
        Initialize the Kalman Filter matrices. This implementation skips the
        control input vector. Symbols used:

        :param Matrix A: state transition matrix - predict next state from current one
        :param Matrix H: observation matrix, calculate measurement from the state
        :param Matrix x: initial estimate of the state
        :param Matrix P: initial estimate of the state covariance matrix
        :param Matrix Q: estimated process covariance
        :param Matrix R: estimated measurement covariance
        :var Matrix I: an identity matrix of size equal to dimension of the state vector
        """
        self.A = A
        self.H = H
        self.x = x
        self.P = P
        self.Q = Q
        self.R = R
        self.I = Matrix.identity(max(x.size()))
        self.measurements = None
        self.counter = None

    @property
    def state(self):
        """ Return current state vector **x** and state covariance **P**.
        Implemented as a property. The user is also allowed to change the
        current state.

        :getter: get tuple (**x**, **P**)
        :setter: set current state"""
        return (self.x, self.P)

    @state.setter
    def state(self, new_state):
        """ Manually set current state along with its covariance. """
        self.x, self.P = new_state

    @property
    def measurements_list(self, digits=5):
        """Return the measurements that are saved in the filter in list format.
        Currently only returns the first entry of each measurement matrix. The
        measurements are returned as floating point numbers rounded to 5 decimal
        digits.

        :return: measurements assigned to the filter
        :rtype: list(float)"""
        return [round(x[0][0], digits) if x is not None
                else x for x in self.measurements]

    def update(self, measurement):
        """ Update the current state prediction of the filter using the
        **measurement**.

        :param measurement: measurement that will be used for the update
        :type measurement: Matrix
        :raises Exception: if size of the measurement is not the same as the shape of
         ``H * x``.
         """
        if measurement.size() != (self.H * self.x).size():
            raise Exception("Wrong vector shape")
        # Update
        y = measurement - self.H * self.x
        S = self.H * self.P * self.H.T + self.R
        K = self.P * self.H.T * S.I
        self.x = self.x + K * y
        self.P = (self.I - K * self.H) * self.P

    def predict(self):
        """Perform the prediction of the next state based on the current state.
        This updates the filters internal state (**x** and **P**). """
        # Predict
        self.x = self.A * self.x
        self.P = self.A * self.P * self.A.T + self.Q

    def step(self, measurement=None, add=False):
        """
        Perform one iteration of the Kalman Filter:

        1. :py:meth:`.update` state from measurement
        2. :py:meth:`.predict` next state from current

        One has to be aware of this order when providing the measurement,
        the supplied measurement should correspond to the filter state before
        the call to :py:meth:`.step`.

        :param measurement: the measurement used to update the state, if ``None`` the filter will only perfom prediction
        :type measurement: Matrix or None
        :param bool add: toggle appending processed measurements to measurement list
         (should generally not be used can result in endless loop).
        :returns: :py:attr:`.state` after the iteration
        """
        # Keep track of measurements that have been used by this filter
        if add:
            try:
                self.measurements.append(measurement)
            except AttributeError:
                # Means this is the first iteration, initial state should be
                # added to measurement list
                self.measurements = [Matrix([self.state[0][0]])]  # ugly, TODO

        if measurement is not None:
            # if measurement has not been supplied no update will be performed
            self.update(measurement)
        self.predict()

        try:
            self.counter += 1
        except TypeError:
            self.counter = 0

        return self.state

    def add_meas(self, measurements):
        """
        Assign measurements to the Kalman Filter object. Necessary for
        iteration over the measurements, but when invoking :py:meth:`.step` by
        hand the measurements need to be supplied to the function call.

        Measurements should be provided as a list of matrices (vector shaped) ready to be
        processed by the filter. The dimensions of each measurement matrix should
        correspond to the size of the matrix one gets when performing matrix
        multiplication between the the observation matrix **H** and the state
        vector **x**.

        :param list(Matrix) measurements: List of measurements in the order in the correct order
        """
        self.measurements = measurements

    def __iter__(self):
        if not self.measurements:
            raise StopIteration
        else:
            return self

    def next(self):
        """
        Return the next iteration of the Kalman Filter. Iteration is done using
        the :py:meth:`step` method. Requires that the list of measurements be
        assigned to the filter first via :py:meth:`.add_meas`. Iteration and calling
        this function consumes the measurements stored in the filter. The user
        should be aware of that and take appropriate steps to ensure that the
        data is not lost to him::

            from copy import copy
            measurements_copy = copy(measurements)
            # or
            measurements_copy = [entry for entry in measurements]
            # now it is safe to assign measurements and iterate over them
            filt.add_meas(measurements)
            for state in filt:
                # process
                pass

        :return: current estimate after 1 iteration as provided by :py:attr:`.state`
        :rtype: tuple(Matrix)
        """
        try:
            current = self.measurements.pop(0)
            ret = self.step(current)
            return ret
        except IndexError:
            raise StopIteration


class TwoWayLKFilter(LKFilter):

    """A bidirectional Kalman Filter. Extends :py:class:`LKFilter` and takes
    the same constructor parameters.

    If the filter object is treated as an iterable, the measurements will be
    iterated over in both directions starting from the last measurements. This
    allows the filter to achieve a higher precision of estimation.

    When measurements are iterated the filter returns two sets of states: the
    measurements iterated over backwards and then forwards.

        >>> len(measurements)
        10
        >>> filt.add_meas(measurements)
        >>> states = list(filt)
        >>> len(states)
        20
        >>> forwards = states[10:]
        >>> backwards = states[:10]

    When the user iterates by calling :py:meth:`.step` by hand he can reverse the
    direction in which the filter is going by calling :py:meth:`.reverse`. This
    is done by reversing the state transition matrix **A**.

    When assigning the measurements to the filter in real time the user can use
    the ``add`` keyword argument of the :py:meth:`.step` method to have the filter save the
    measurements while stepping. Once all measurements have been iterated over the
    filter can be reversed and iterate over the measurements once more to get a
    better estimate.

        >>> for measurement in data:
        ...     filt.step(measurement, add=True)
        ...
        >>> filt.reverse()
        >>> better_estimates = list(filt)
        >>> len(better_estimates) == len(data)
        True

    """

    def __init__(self, *arg, **kwg):
        super(TwoWayLKFilter, self).__init__(*arg, **kwg)
        self.reverse_measurements = []
        # Flag that reflects whether filter is iterating forward or backward
        self.rev = False

    def add_meas(self, measurements):
        """Stores the measurements to be iterated over in the filter."""
        self.reverse_measurements = collections.deque(measurements)
        self.measurements = collections.deque(reversed(measurements))

    def reverse(self):
        """Reverses the direction in which the filter is currently iterating.
        This performs a matrix inversion of the matrix state transition matrix
        **A**."""
        self.A = self.A.I
        self.rev = not self.rev

    def __iter__(self):
        if not self.measurements:
            raise StopIteration
        else:
            # first iterating backwards, so need inverse transition
            # matrix
            self.reverse()
            return self

    def next(self):
        """Return the next iteration of the two-way Kalman Filter. First
        iterates over the measurements in reverse and then in the forward
        direction."""
        try:
            current = self.reverse_measurements.pop()
            ret = self.step(current)
            return ret
        except IndexError:
            # Finished iterating from the back, now time for forward.
            # iteration.
            # Exchange the measurements that are being iterated over.
            self.reverse_measurements, self.measurements = (
                self.measurements, self.reverse_measurements)
            # if reverse_measurements is now empty it means we already iterated
            # forward, stop iteration.
            if len(self.reverse_measurements) == 0:
                raise StopIteration
            self.reverse()
            # resume iteration
            return self.next()
