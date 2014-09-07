""" Kalman Filter module """
# pylint: disable=C0103,R0192
from matrix import Matrix
import collections


class LKFilter(object):

    """
    A Linear Kalman Filter implementation.

    For more details on this implementation go to:
    http://greg.czerniak.info/guides/kalman1/
    """

    def __init__(self, A, H, x, P, Q, R):
        """
        Initialize the Kalman Filter matrices. This implementation skips the
        control input vector. Symbols used:

        * A - state transition matrix - predict next state from current one
        * H - measurement matrix, calculate measurement from the state
        * x - initial estimate of the state
        * P - initial estimate of the state covariance matrix
        * Q - estimated process covariance
        * R - estimated measurement covariance
        * I - an identity matrix of size equal to dimension of the state vector
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
        """ Return current state vector and state covariance. """
        return (self.x, self.P)

    @state.setter
    def state(self, new_state):
        """ Manually set current state along with its covariance. """
        self.x, self.P = new_state

    @property
    def measurements_list(self, digits=5):
        """Return 1D measurements in list instead of matrix form."""
        return [round(x[0][0], digits) if x is not None
                else x for x in self.measurements]

    def update(self, measurement):
        """ Update current state using the measurement. """
        if measurement.size() != (self.H * self.x).size():
            raise Exception("Wrong vector shape")
        # Update
        y = measurement - self.H * self.x
        S = self.H * self.P * self.H.T + self.R
        K = self.P * self.H.T * S.I
        self.x = self.x + K * y
        self.P = (self.I - K * self.H) * self.P

    def predict(self):
        """ Predict the next state based on current state. """
        # Predict
        self.x = self.A * self.x
        self.P = self.A * self.P * self.A.T + self.Q

    def step(self, measurement=None, add=False):
        """
        Perform one iteration of the Kalman Filter:

            1. update state from measurement
            2. predict next state from current

        Depending on what is expected the order of these operations can also
        be inverted.
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
        iteration, does nothing if invoking :py:meth:step by hand.
        """
        self.measurements = measurements

    def __iter__(self):
        if not self.measurements:
            raise StopIteration
        else:
            return self

    def next(self):
        """
        Return the next iteration of the Kalman Filter. Requires that the
        list of measurements be assigned to the filter first via
        :py:meth:add_meas.
        """
        try:
            current = self.measurements.pop(0)
            ret = self.step(current)
            return ret
        except IndexError:
            raise StopIteration


class TwoWayLKFilter(LKFilter):
    """A bidirectional Kalman Filter: the measurements will be iterated in both
    directions starting from the last measurements. This allows the filter to
    achieve a higher precision of estimation."""

    def __init__(self, *arg, **kwg):
        super(TwoWayLKFilter, self).__init__(*arg, **kwg)
        self.reverse_measurements = []
        # Flag that reflects whether filter is iterating forward or backward
        self.rev = False

    def add_meas(self, measurements):
        """Assign measurements to filter."""
        self.reverse_measurements = collections.deque(measurements)
        self.measurements = collections.deque(reversed(measurements))

    def reverse(self):
        """Reverse the direction in which the filter is currently iterating."""
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
        iterates over the measurements in reverse and then in the proper
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
